# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Vision enrichment pipeline orchestrator."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import structlog

from agentic.cse_client import CSEClient
from agentic.search_client_factory import create_search_client
from agentic.enrichment.gpt_allowlist_planner import GPTAllowlistPlanner
from agentic.enrichment.scraper import WebScraper
from agentic.llm import LLMClient
from agentic.schemas import Plan, QuerySpec, StopConditions, Budget, QualityGates
from agentic.scoring import ResultScorer
from agentic.vision.gemini_client import GeminiClient
from agentic.vision.vision_client import VisionClient
from apps.api.schemas.vision_enrichment import DocumentJSONL, AllowlistPlan
from common.env_readers import load_yaml_with_env
from common.settings import settings
from db.upload_dao import VisionUploadDAO
from db.session import DatabaseSession
from ingestion.chunkers import TokenAwareChunker
from ingestion.txt_emitter import TXTEmitter
from pipelines.agentic_controller import run_agentic_search
from vector.qdrant_loader import push_doc_hashes
from db.dao import get_chunks_by_hashes, get_manifests_by_hashes, mark_manifest_vector, ChunkManifestDAO, ChunkStoreDAO

logger = structlog.get_logger()


class EnrichmentPipeline:
    """Orchestrates the full vision enrichment pipeline."""
    
    def __init__(self, config: Dict):
        """
        Initialize pipeline.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize clients
        self.vision_client = VisionClient(api_key=settings.google_api_key)
        self.llm_client = LLMClient(
            api_key=settings.openai_api_key,
            model=config.get("llm", {}).get("model", "gpt-4o-mini"),
            temperature=config.get("llm", {}).get("temperature", 0),
        )
        # Pass llm_client to GeminiClient for GPT-based hypothesis generation
        self.gemini_client = GeminiClient(
            api_key=settings.google_api_key,
            llm_client=self.llm_client
        )
        self.scraper = WebScraper(
            timeout=config.get("scraper", {}).get("timeout", 20)
        )
        
        # Initialize emitter
        txt_output_base = config.get("output", {}).get("txt_base_dir", "data/output/enrichment_txt")
        self.txt_emitter = TXTEmitter(output_base_dir=txt_output_base)
        
        # Initialize chunker
        self.chunker = TokenAwareChunker(
            max_tokens=config.get("chunker", {}).get("max_tokens", 512),
            overlap_tokens=config.get("chunker", {}).get("overlap_tokens", 50),
            min_tokens=config.get("chunker", {}).get("min_tokens", 100),
        )
        
        self.db_session = DatabaseSession()
    
    def run(self, upload_id: str) -> Dict:
        """
        Run complete enrichment pipeline.
        
        Args:
            upload_id: Upload ID to process
            
        Returns:
            Result dictionary with stats
        """
        logger.info("enrichment_pipeline_start", upload_id=upload_id)
        
        try:
            with next(self.db_session.get_session()) as session:
                # Load upload record
                upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
                
                if not upload:
                    raise ValueError(f"Upload not found: {upload_id}")
                
                # Update status
                VisionUploadDAO.update_status(session, upload_id, "processing")
                session.commit()
                
                # ✅ CACHE CHECK: Se JSONL já existe, pular OCR + Gemini
                jsonl_path = Path("data/output/jsonl") / f"{upload_id}.jsonl"
                
                if upload.jsonl_path and Path(upload.jsonl_path).exists():
                    # Cache HIT! Reutilizar JSONL anterior
                    jsonl_path = Path(upload.jsonl_path)
                    logger.info(
                        "enrichment_cache_hit_jsonl",
                        upload_id=upload_id,
                        path=str(jsonl_path),
                        msg="Skipping OCR + Gemini (using cached JSONL)"
                    )
                    
                    # Marcar estágios como completed (já foram processados)
                    VisionUploadDAO.update_stage(session, upload_id, "ocr", "completed")
                    VisionUploadDAO.update_stage(session, upload_id, "multimodal", "completed")
                    session.commit()
                    
                else:
                    # Cache MISS! Processar OCR + Gemini
                    logger.info("enrichment_cache_miss", upload_id=upload_id, msg="Processing OCR + Gemini")
                    
                    # Stage 1: OCR
                    logger.info("enrichment_stage_ocr", upload_id=upload_id)
                    VisionUploadDAO.update_stage(session, upload_id, "ocr", "running")
                    session.commit()
                    
                    page_ocr_results = self.vision_client.extract_text(upload.file_path)
                    
                    VisionUploadDAO.update_stage(session, upload_id, "ocr", "completed")
                    session.commit()
                    
                    # Stage 2: Multimodal (Gemini)
                    logger.info("enrichment_stage_multimodal", upload_id=upload_id)
                    VisionUploadDAO.update_stage(session, upload_id, "multimodal", "running")
                    session.commit()
                    
                    jsonl_lines = []
                    for page_ocr in page_ocr_results:
                        figures = self.gemini_client.describe_figures(upload.file_path, page_ocr)
                        inferences = self.gemini_client.guided_inferences(upload.file_path, page_ocr)
                        
                        doc_line = DocumentJSONL(
                            doc_id=upload_id,
                            page=page_ocr.page,
                            text=page_ocr.text,
                            figures=figures,
                            guided_inferences=inferences,
                            meta={"filename": upload.original_filename},
                        )
                        jsonl_lines.append(doc_line)
                    
                    # Write JSONL
                    jsonl_dir = Path("data/output/jsonl")
                    jsonl_dir.mkdir(parents=True, exist_ok=True)
                    jsonl_path = jsonl_dir / f"{upload_id}.jsonl"
                    
                    with open(jsonl_path, "w", encoding="utf-8") as f:
                        for line in jsonl_lines:
                            f.write(line.model_dump_json() + "\n")
                    
                    VisionUploadDAO.update_artifacts(session, upload_id, jsonl_path=str(jsonl_path))
                    VisionUploadDAO.update_stage(session, upload_id, "multimodal", "completed")
                    session.commit()
                    
                    logger.info("enrichment_jsonl_written", path=str(jsonl_path), lines=len(jsonl_lines))
                
                # Stage 3: Allowlist planning (GPT)
                logger.info("enrichment_stage_allowlist", upload_id=upload_id)
                VisionUploadDAO.update_stage(session, upload_id, "allowlist", "running")
                session.commit()
                
                planner = GPTAllowlistPlanner(self.llm_client)
                allowlist_plan = planner.plan(str(jsonl_path))
                
                VisionUploadDAO.update_stage(session, upload_id, "allowlist", "completed")
                session.commit()
                
                # Stage 4: Agentic Search
                logger.info("enrichment_stage_agentic", upload_id=upload_id)
                VisionUploadDAO.update_stage(session, upload_id, "agentic", "running")
                session.commit()
                
                agentic_result = self._run_agentic_search(session, allowlist_plan)
                
                VisionUploadDAO.update_artifacts(session, upload_id, plan_id=agentic_result.plan_id)
                VisionUploadDAO.update_stage(session, upload_id, "agentic", "completed")
                session.commit()
                
                logger.info(
                    "enrichment_agentic_done",
                    plan_id=agentic_result.plan_id,
                    approved=agentic_result.approved_total,
                )
                
                # ✅ PAUSA AQUI! Aguardar seleção do usuário
                # Stage 5-6 serão executadas via /vision/scrape/{upload_id}
                VisionUploadDAO.update_stage(session, upload_id, "scrape", "pending")
                VisionUploadDAO.update_stage(session, upload_id, "vector", "pending")
                VisionUploadDAO.update_status(session, upload_id, "awaiting_review")
                session.commit()
                
                logger.info("enrichment_pipeline_done", upload_id=upload_id)
                
                return {
                    "ok": True,
                    "upload_id": upload_id,
                    "jsonl_path": str(jsonl_path),
                    "plan_id": agentic_result.plan_id,
                    "approved_urls": agentic_result.approved_total,
                    "status": "awaiting_review",
                    "message": "Agentic search completed. Review URLs before scraping.",
                }
        
        except Exception as e:
            logger.error("enrichment_pipeline_failed", upload_id=upload_id, error=str(e))
            
            try:
                with next(self.db_session.get_session()) as session:
                    VisionUploadDAO.update_status(
                        session,
                        upload_id,
                        "failed",
                        error_message=str(e),
                    )
                    session.commit()
            except Exception:
                pass
            
            return {
                "ok": False,
                "upload_id": upload_id,
                "error": str(e),
            }
    
    def _run_agentic_search(self, session, allowlist_plan: AllowlistPlan):
        """Run agentic search with allowlist plan."""
        # Convert AllowlistPlan to agentic Plan
        queries = [
            QuerySpec(q=q.q, why=q.why if hasattr(q, 'why') else "", k=10)
            for q in allowlist_plan.queries
        ]
        
        stop = StopConditions(
            min_approved=allowlist_plan.stop.get("min_approved", 10),
            max_iterations=allowlist_plan.stop.get("max_iterations", 3),
            max_queries_per_iter=allowlist_plan.stop.get("max_queries_per_iter", 4),
        )
        
        budget = Budget(
            max_cse_calls=20,
            ttl_days=7,
        )
        
        quality_gates = QualityGates(
            must_types=allowlist_plan.quality_gates.get("must_types", ["pdf", "html"]),
            max_age_years=allowlist_plan.quality_gates.get("max_age_years", 3),
            min_score=allowlist_plan.quality_gates.get("min_score", 0.7),
            min_anchor_signals=allowlist_plan.quality_gates.get("min_anchor_signals", 0),
        )
        
        plan = Plan(
            goal=allowlist_plan.goal,
            queries=queries,
            allow_domains=allowlist_plan.allow_domains,
            deny_patterns=[],
            stop=stop,
            budget=budget,
            quality_gates=quality_gates,
        )
        
        # Initialize agentic clients
        cse_config = load_yaml_with_env("configs/cse.yaml")
        
        # ✅ Use factory to support CSE or Vertex AI Search
        from agentic.search_client_factory import create_search_client
        
        cse = create_search_client(cse_config)
        
        # ✅ IMPORTANTE: Usar allow_domains do PLAN (gerado pelo GPT), não do config!
        scorer = ResultScorer(
            cse_config,
            authority_domains=plan.allow_domains  # ← Domínios do GPT/Plan!
        )
        
        logger.info(
            "enrichment_scorer_configured",
            authority_domains=plan.allow_domains,
            msg="Using domains from LLM plan, not hardcoded config"
        )
        
        # Run agentic search
        result = run_agentic_search(plan, session, cse, self.llm_client, scorer)
        
        return result
    
    def _run_scraping_and_vector_phase(
        self,
        upload_id: str,
        selected_urls: Optional[List[str]] = None,
    ):
        """
        Run scraping and vector phases (Stage 5-6).
        
        Called after user reviews and selects URLs.
        
        Args:
            upload_id: Upload ID
            selected_urls: URLs to scrape (None = all approved)
        """
        logger.info("enrichment_scraping_phase_start", upload_id=upload_id)
        
        try:
            with next(self.db_session.get_session()) as session:
                upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
                
                if not upload or not upload.plan_id:
                    raise ValueError(f"Upload or plan not found: {upload_id}")
                
                # Get approved URLs if not provided
                if selected_urls is None:
                    from db.dao import AgenticIterDAO
                    
                    iters = AgenticIterDAO.get_iters(session, upload.plan_id)
                    all_urls = set()
                    for it in iters:
                        all_urls.update(it.get("approved_urls", []))
                    selected_urls = list(all_urls)
                
                logger.info("enrichment_urls_to_scrape", count=len(selected_urls))
                
                # Stage 5: Scrape
                VisionUploadDAO.update_stage(session, upload_id, "scrape", "running")
                session.commit()
                
                scraped_count = self._scrape_and_emit(upload_id, selected_urls)
                
                VisionUploadDAO.update_stage(session, upload_id, "scrape", "completed")
                session.commit()
                
                logger.info("enrichment_scrape_done", scraped=scraped_count)
                
                # Stage 6: Mark vector as pending (will be triggered by user)
                VisionUploadDAO.update_stage(session, upload_id, "vector", "pending")
                VisionUploadDAO.update_status(session, upload_id, "completed")
                session.commit()
                
                logger.info("enrichment_scraping_phase_done", upload_id=upload_id)
        
        except Exception as e:
            logger.error("enrichment_scraping_phase_failed", upload_id=upload_id, error=str(e))
            
            try:
                with next(self.db_session.get_session()) as session:
                    VisionUploadDAO.update_stage(session, upload_id, "scrape", "failed")
                    VisionUploadDAO.update_status(session, upload_id, "failed", error_message=str(e))
                    session.commit()
            except Exception:
                pass
    
    def _scrape_and_emit(self, upload_id: str, urls: List[str]) -> int:
        """Scrape URLs and emit TXT files."""
        scraped = 0
        
        for idx, url in enumerate(urls):
            try:
                # Check if already exists (by hash)
                scrape_result = self.scraper.scrape(url)
                
                if not scrape_result.get("ok"):
                    logger.warning("enrichment_scrape_skip", url=url, reason=scrape_result.get("error"))
                    continue
                
                doc_hash = scrape_result["doc_hash"]
                
                # Check idempotency
                if self.txt_emitter.check_exists(upload_id, doc_hash):
                    logger.info("enrichment_txt_exists_skip", doc_hash=doc_hash[:16])
                    continue
                
                # Emit TXT file
                self.txt_emitter.emit(
                    upload_id=upload_id,
                    doc_num=idx + 1,
                    url=scrape_result["url"],
                    domain=scrape_result["domain"],
                    fetched_at=scrape_result["fetched_at"],
                    doc_hash=doc_hash,
                    text=scrape_result["text"],
                )
                
                scraped += 1
            
            except Exception as e:
                logger.error("enrichment_scrape_emit_failed", url=url, error=str(e))
                continue
        
        return scraped
    
    def push_to_vector(self, upload_id: str, collection: str = "kb_regulatory", overwrite: bool = False) -> Dict:
        """
        Push scraped documents to vector database.
        
        Args:
            upload_id: Upload ID
            collection: Qdrant collection name
            overwrite: Overwrite existing vectors
            
        Returns:
            Result dictionary
        """
        logger.info("enrichment_vector_push_start", upload_id=upload_id, collection=collection)
        
        try:
            with next(self.db_session.get_session()) as session:
                # Load upload
                upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
                
                if not upload:
                    raise ValueError(f"Upload not found: {upload_id}")
                
                # Update stage
                VisionUploadDAO.update_stage(session, upload_id, "vector", "running")
                session.commit()
                
                # Find TXT files
                txt_dir = Path(self.txt_emitter.output_base_dir) / upload_id
                
                if not txt_dir.exists():
                    raise ValueError(f"TXT directory not found: {txt_dir}")
                
                txt_files = list(txt_dir.glob("*.txt"))
                
                if not txt_files:
                    raise ValueError(f"No TXT files found in {txt_dir}")
                
                logger.info("enrichment_vector_processing", files=len(txt_files))
                
                # Process each TXT file
                doc_hashes = []
                
                for txt_file in txt_files:
                    try:
                        # Read file
                        with open(txt_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Parse metadata
                        meta, text = self._parse_txt_file(content)
                        
                        doc_hash = meta["doc_hash"]
                        url = meta["url"]
                        
                        # Chunk text
                        chunks = self.chunker.chunk(text, doc_id=doc_hash)
                        
                        # Save to database
                        import hashlib
                        
                        # ✅ Tag como 'enrichment' para rastreabilidade
                        ChunkManifestDAO.upsert(
                            session,
                            doc_hash=doc_hash,
                            canonical_url=url,
                            source_file=str(txt_file),
                            doc_type="html",
                            chunk_count=len(chunks),
                            status="done",
                            meta=json.dumps({**meta, "upload_id": upload_id, "source": "enrichment"}),
                            source_pipeline="enrichment",
                        )
                        
                        ChunkStoreDAO.bulk_create(session, doc_hash, chunks)
                        
                        doc_hashes.append(doc_hash)
                        
                        logger.info("enrichment_chunks_saved", doc_hash=doc_hash[:16], chunks=len(chunks))
                    
                    except Exception as e:
                        logger.error("enrichment_chunk_failed", file=txt_file.name, error=str(e))
                        continue
                
                session.commit()
                
                # Push to vector
                if doc_hashes:
                    result = push_doc_hashes(
                        doc_hashes=doc_hashes,
                        collection=collection,
                        batch_size=64,
                        overwrite=overwrite,
                        fetch_chunks_fn=get_chunks_by_hashes,
                        fetch_manifests_fn=get_manifests_by_hashes,
                        mark_manifest_vector_fn=mark_manifest_vector,
                    )
                    
                    logger.info(
                        "enrichment_vector_pushed",
                        pushed=result["pushed"],
                        skipped=result["skipped"],
                    )
                    
                    VisionUploadDAO.update_stage(session, upload_id, "vector", "completed")
                    session.commit()
                    
                    return {
                        "ok": True,
                        "upload_id": upload_id,
                        "doc_hashes": doc_hashes,
                        "pushed": result["pushed"],
                        "skipped": result["skipped"],
                    }
                else:
                    raise ValueError("No documents to push")
        
        except Exception as e:
            logger.error("enrichment_vector_push_failed", upload_id=upload_id, error=str(e))
            
            try:
                with next(self.db_session.get_session()) as session:
                    VisionUploadDAO.update_stage(session, upload_id, "vector", "failed")
                    session.commit()
            except Exception:
                pass
            
            return {
                "ok": False,
                "upload_id": upload_id,
                "error": str(e),
            }
    
    def _parse_txt_file(self, content: str) -> tuple:
        """
        Parse TXT file with metadata header.
        
        Args:
            content: File content
            
        Returns:
            Tuple of (metadata_dict, text)
        """
        lines = content.split("\n")
        
        meta = {}
        text_lines = []
        in_meta = False
        in_content = False
        
        for line in lines:
            if line.strip() == "===META===":
                in_meta = True
                continue
            elif line.strip() == "===CONTENT===":
                in_meta = False
                in_content = True
                continue
            
            if in_meta:
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip()
            elif in_content:
                text_lines.append(line)
        
        text = "\n".join(text_lines)
        
        return meta, text

