"""PDF document ingestor with LLM-guided chunking."""

import hashlib
import structlog
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

import pdfplumber
import requests
from pypdf import PdfReader
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic.llm import LLMClient
from agentic.normalize import extract_domain
from ingestion.anchors import AnchorDetector
from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter

logger = structlog.get_logger()


class PDFIngestor:
    """Ingest PDF documents with intelligent chunking."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        llm_client: LLMClient,
        chunker: TokenAwareChunker,
        emitter: JSONLEmitter,
    ):
        """
        Initialize PDF ingestor.
        
        Args:
            config: Ingest configuration
            llm_client: LLM client for marker suggestions
            chunker: Token-aware chunker
            emitter: Output emitter
        """
        self.config = config
        self.llm = llm_client
        self.chunker = chunker
        self.emitter = emitter
        self.download_dir = Path(config["download"]["download_dir"])
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = config["download"]["timeout"]
        self.user_agent = config["download"]["user_agent"]
        self.max_pages_preview = config["pdf"]["max_pages_preview"]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def download(
        self,
        url: str,
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
    ) -> Optional[Path]:
        """
        Download PDF with conditional requests.
        
        Args:
            url: PDF URL
            etag: Previous ETag for conditional request
            last_modified: Previous Last-Modified for conditional request
            
        Returns:
            Path to downloaded file, or None if not modified
        """
        headers = {"User-Agent": self.user_agent}
        
        # Conditional headers
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
        
        # Not modified
        if response.status_code == 304:
            return None
        
        response.raise_for_status()
        
        # Save to file
        filename = f"{hash(url)}.pdf"
        file_path = self.download_dir / filename
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return file_path
    
    def extract_text(self, pdf_path: Path) -> List[str]:
        """
        Extract text from PDF pages.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of page texts
        """
        pages = []
        
        try:
            # Try pdfplumber first
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    pages.append(text)
        except Exception:
            # Fallback to pypdf
            if self.config["pdf"]["fallback_to_pypdf"]:
                try:
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        text = page.extract_text() or ""
                        pages.append(text)
                except Exception:
                    pass
        
        return pages
    
    def ingest(
        self,
        url: str,
        title: Optional[str],
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        expected_type: str = "pdf",
    ) -> bool:
        """
        Ingest PDF document.
        
        Args:
            url: PDF URL
            title: Document title
            etag: Previous ETag
            last_modified: Previous Last-Modified
            expected_type: Expected document type (should be 'pdf')
            
        Returns:
            True if successfully ingested
        """
        # Validate expected type
        if expected_type and expected_type != "pdf":
            logger.error(
                "pdf_type_mismatch",
                url=url,
                expected=expected_type,
                executor="pdf",
            )
            return False
        
        try:
            # Download
            logger.info("pdf_download_start", url=url)
            pdf_path = self.download(url, etag, last_modified)
            
            if pdf_path is None:
                # Not modified, skip
                logger.info("pdf_not_modified", url=url)
                return False
            
            logger.info("pdf_downloaded", url=url, path=str(pdf_path))
            
            # Extract text
            logger.info("pdf_extract_start", url=url)
            pages = self.extract_text(pdf_path)
            
            if not pages:
                logger.warning("pdf_no_text_extracted", url=url)
                return False
            
            logger.info("pdf_extracted", url=url, num_pages=len(pages))
            
            # Get LLM marker suggestions
            logger.info("pdf_markers_start", url=url)
            domain = extract_domain(url)
            pages_preview = pages[:self.max_pages_preview]
            
            markers = self.llm.suggest_pdf_markers(
                title=title or url,
                pages_preview=pages_preview,
                domain=domain,
            )
            logger.info("pdf_markers_received", url=url, num_markers=len(markers) if markers else 0)
            
            # Detect anchors and segment
            logger.info("pdf_chunking_start", url=url)
            full_text = "\n\n".join(pages)
            
            if markers:
                detector = AnchorDetector(markers)
                segments = detector.segment_by_anchors(full_text)
                chunks = self.chunker.chunk_with_anchors(segments)
            else:
                # No markers, just chunk directly
                chunks = self.chunker.chunk(full_text)
            
            logger.info("pdf_chunked", url=url, num_chunks=len(chunks))
            
            # Emit chunks
            logger.info("pdf_emit_start", url=url)
            self.emitter.emit_chunks(
                chunks=chunks,
                source_url=url,
                source_file=str(pdf_path),
            )
            logger.info("pdf_ingest_complete", url=url)
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(
                "pdf_download_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "pdf_ingest_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for hashing."""
        parsed = urlparse(url)
        # Remove fragment, normalize path
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or '/',
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        return normalized
    
    def ingest_one(
        self,
        url: str,
        title: Optional[str] = None,
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Process single PDF URL and return chunks in memory.
        
        This method downloads, extracts, detects anchors, and chunks a PDF,
        returning the results without writing to disk (JSONL).
        
        Args:
            url: PDF URL to process
            title: Document title (optional)
            etag: Previous ETag for conditional download
            last_modified: Previous Last-Modified for conditional download
            
        Returns:
            Dictionary with:
            {
                "ok": bool,
                "doc_hash": str,
                "chunks": [{"chunk_id": int, "text": str, "anchors": {...}, "metadata": {...}}],
                "meta": {
                    "final_type": "pdf",
                    "num_pages": int,
                    "num_anchors": int,
                    "etag": str,
                    "last_modified": str,
                }
            }
        """
        try:
            logger.info("pdf_ingest_one_start", url=url)
            
            # 1. Download PDF
            pdf_path = self.download(url, etag, last_modified)
            
            if pdf_path is None:
                # Not modified
                logger.info("pdf_not_modified", url=url)
                return {
                    "ok": False,
                    "reason": "not_modified",
                    "doc_hash": None,
                    "chunks": [],
                    "meta": {}
                }
            
            # 2. Extract text by pages
            pages = self.extract_text(pdf_path)
            
            if not pages:
                logger.warning("pdf_no_text", url=url)
                return {
                    "ok": False,
                    "reason": "no_text_extracted",
                    "doc_hash": None,
                    "chunks": [],
                    "meta": {}
                }
            
            logger.info("pdf_extracted", url=url, num_pages=len(pages))
            
            # 3. Get LLM marker suggestions from first pages
            domain = extract_domain(url)
            pages_preview = pages[:self.max_pages_preview]
            
            markers = self.llm.suggest_pdf_markers(
                title=title or url,
                pages_preview=pages_preview,
                domain=domain,
            )
            
            logger.info("pdf_markers", url=url, num_markers=len(markers) if markers else 0)
            
            # 4. Chunk with anchors or fallback to token-aware
            full_text = "\n\n".join(pages)
            
            if markers:
                detector = AnchorDetector(markers)
                segments = detector.segment_by_anchors(full_text)
                chunks = self.chunker.chunk_with_anchors(segments)
            else:
                chunks = self.chunker.chunk(full_text)
            
            logger.info("pdf_chunked", url=url, num_chunks=len(chunks))
            
            # 5. Add page hints to chunks (map by character offset)
            # Simple heuristic: estimate page by char position
            total_chars = len(full_text)
            avg_chars_per_page = total_chars / len(pages) if pages else 1
            
            for chunk in chunks:
                # Estimate page based on chunk start position
                start_pos = chunk.get("metadata", {}).get("start_char", 0)
                estimated_page = int(start_pos / avg_chars_per_page) + 1
                
                chunk["metadata"] = chunk.get("metadata", {})
                chunk["metadata"]["page_hint"] = min(estimated_page, len(pages))
                chunk["metadata"]["num_pages"] = len(pages)
                chunk["metadata"]["source_type"] = "pdf"
            
            # 6. Generate doc_hash
            canonical = self._normalize_url(url)
            hash_input = canonical + (last_modified.isoformat() if last_modified else "") + "pdf"
            doc_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            
            # 7. Return result
            return {
                "ok": True,
                "doc_hash": doc_hash,
                "chunks": chunks,
                "meta": {
                    "final_type": "pdf",
                    "num_pages": len(pages),
                    "num_anchors": len(markers) if markers else 0,
                    "etag": etag,
                    "last_modified": last_modified.isoformat() if last_modified else None,
                    "source_file": str(pdf_path),
                }
            }
        
        except Exception as e:
            logger.error("pdf_ingest_one_failed", url=url, error=str(e))
            return {
                "ok": False,
                "reason": str(e),
                "doc_hash": None,
                "chunks": [],
                "meta": {}
            }

