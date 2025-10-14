"""Ingest pipeline: read DB → diff → route → ingest."""

import argparse
import structlog
from typing import Any, Dict, List

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from agentic.llm import LLMClient
from common.env_readers import load_yaml_with_env

# Load .env into os.environ
load_dotenv()
from db.dao import DocumentCatalogDAO
from db.models import DocumentCatalog
from db.session import DatabaseSession
from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter
from pipelines.executors.html_ingestor import HTMLIngestor
from pipelines.executors.pdf_ingestor import PDFIngestor
from pipelines.executors.zip_ingestor import ZIPIngestor
from pipelines.routers import DocumentRouter

logger = structlog.get_logger()


class IngestPipeline:
    """Execute ingest pipeline: diff → route → process → emit."""
    
    def __init__(self, ingest_config: Dict[str, Any], db_config: Dict[str, Any]):
        """
        Initialize ingest pipeline.
        
        Args:
            ingest_config: Ingest configuration from ingest.yaml
            db_config: DB configuration from db.yaml
        """
        self.ingest_config = ingest_config
        self.db_config = db_config
        
        # Initialize LLM
        self.llm = LLMClient(
            api_key=ingest_config["llm"]["api_key"],
            model=ingest_config["llm"]["model"],
            temperature=ingest_config["llm"]["temperature"],
            max_tokens=ingest_config["llm"]["max_tokens"],
            timeout=ingest_config["llm"]["timeout"],
        )
        
        # Initialize router
        self.router = DocumentRouter(self.llm)
        
        # Initialize chunker
        chunking_cfg = ingest_config["chunking"]
        self.chunker = TokenAwareChunker(
            min_tokens=chunking_cfg["min_tokens"],
            max_tokens=chunking_cfg["max_tokens"],
            overlap_tokens=chunking_cfg["overlap_tokens"],
            encoding=chunking_cfg["encoding"],
        )
        
        # Initialize emitter
        output_cfg = ingest_config["output"]
        output_path = f"{output_cfg['output_dir']}/{output_cfg['filename']}"
        self.emitter = JSONLEmitter(output_path)
        
        # Initialize executors
        self.pdf_ingestor = PDFIngestor(ingest_config, self.llm, self.chunker, self.emitter)
        self.zip_ingestor = ZIPIngestor(ingest_config, self.chunker, self.emitter)
        self.html_ingestor = HTMLIngestor(ingest_config, self.chunker, self.emitter, self.llm)
        
        self.db_session = DatabaseSession()
    
    def execute(self, limit: int = 100) -> Dict[str, int]:
        """
        Execute ingest pipeline.
        
        Args:
            limit: Max documents to process
            
        Returns:
            Stats dict with counts
        """
        logger.info("ingest_pipeline_start", limit=limit)
        
        stats = {
            "total": 0,
            "new": 0,
            "changed": 0,
            "same": 0,
            "success": 0,
            "failed": 0,
        }
        
        with next(self.db_session.get_session()) as session:
            # Get pending/changed documents
            documents = DocumentCatalogDAO.get_pending_or_changed(session, limit=limit)
            
            stats["total"] = len(documents)
            logger.info("documents_to_process", count=stats["total"])
            
            for doc in documents:
                # Determine if NEW or CHANGED
                if doc.ingest_status == "pending":
                    status = "NEW"
                    stats["new"] += 1
                else:
                    status = "CHANGED"
                    stats["changed"] += 1
                
                logger.info("processing_document", url=doc.canonical_url, status=status)
                
                # Route document (trust DB final_type first)
                doc_type = self.router.route_item(
                    url=doc.canonical_url,
                    content_type=doc.content_type,
                    title=doc.title,
                    snippet=None,
                    final_type=getattr(doc, 'final_type', None),
                )
                
                logger.info("routed", url=doc.canonical_url, type=doc_type)
                
                # Ingest based on type
                result = self._ingest_document(session, doc, doc_type)
                
                # Handle result (can be bool for PDF/ZIP or dict for HTML)
                if isinstance(result, dict):
                    success = result.get("ok", False)
                    next_type = result.get("next_type")
                    next_url = result.get("next_url")
                    
                    # If HTML detected a PDF wrapper, log it
                    if next_type == "pdf" and next_url:
                        logger.info(
                            "pdf_wrapper_reroute",
                            original_url=doc.canonical_url,
                            pdf_url=next_url,
                        )
                        # Could enqueue PDF for processing here
                        # For now, just mark as failed with note
                        stats["failed"] += 1
                        DocumentCatalogDAO.mark_ingested(
                            session,
                            doc.canonical_url,
                            status="failed",
                            error_message=f"PDF wrapper detected: {next_url}",
                        )
                    elif success:
                        stats["success"] += 1
                        DocumentCatalogDAO.mark_ingested(session, doc.canonical_url, status="completed")
                    else:
                        stats["failed"] += 1
                        DocumentCatalogDAO.mark_ingested(
                            session,
                            doc.canonical_url,
                            status="failed",
                            error_message="Ingestion failed",
                        )
                else:
                    # Legacy bool return (PDF/ZIP ingestors)
                    success = result
                    if success:
                        stats["success"] += 1
                        DocumentCatalogDAO.mark_ingested(session, doc.canonical_url, status="completed")
                    else:
                        stats["failed"] += 1
                        DocumentCatalogDAO.mark_ingested(
                            session,
                            doc.canonical_url,
                            status="failed",
                            error_message="Ingestion failed",
                        )
                
                session.commit()
        
        logger.info("ingest_pipeline_complete", stats=stats)
        
        return stats
    
    def _ingest_document(
        self,
        session: Session,
        doc: DocumentCatalog,
        doc_type: str,
    ) -> bool | Dict[str, Any]:
        """
        Ingest a single document.
        
        Args:
            session: DB session
            doc: DocumentCatalog record
            doc_type: Document type ('pdf', 'zip', 'html')
            
        Returns:
            True if successful
        """
        try:
            if doc_type == "pdf":
                return self.pdf_ingestor.ingest(
                    url=doc.canonical_url,
                    title=doc.title,
                    etag=doc.etag,
                    last_modified=doc.last_modified,
                    expected_type=doc_type,
                )
            elif doc_type == "zip":
                return self.zip_ingestor.ingest(
                    url=doc.canonical_url,
                    title=doc.title,
                    etag=doc.etag,
                    last_modified=doc.last_modified,
                    expected_type=doc_type,
                )
            elif doc_type == "html":
                return self.html_ingestor.ingest(
                    url=doc.canonical_url,
                    title=doc.title,
                    etag=doc.etag,
                    last_modified=doc.last_modified,
                    expected_type=doc_type,
                )
            else:
                logger.error("unknown_doc_type", url=doc.canonical_url, type=doc_type)
                return False
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(
                "ingest_error",
                url=doc.canonical_url,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=error_trace,
            )
            return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run ingest pipeline")
    parser.add_argument("--config", default="configs/ingest.yaml", help="Ingest config path")
    parser.add_argument("--db", default="configs/db.yaml", help="DB config path")
    parser.add_argument("--limit", type=int, default=None, help="Max documents to process (overrides config)")
    
    args = parser.parse_args()
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    
    # Load configs
    ingest_config = load_yaml_with_env(args.config)
    db_config = load_yaml_with_env(args.db)
    
    # Get limit from CLI or config
    limit = args.limit if args.limit is not None else ingest_config.get("pipeline", {}).get("limit", 100)
    
    # Run pipeline
    pipeline = IngestPipeline(ingest_config, db_config)
    stats = pipeline.execute(limit=limit)
    
    print(f"Ingest complete: {stats}")


if __name__ == "__main__":
    main()

