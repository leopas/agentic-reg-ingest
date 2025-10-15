# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""HTML document ingestor with LLM structure extraction and PDF wrapper detection."""

import structlog
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic.html_extract import clean_html_to_excerpt, is_probably_pdf_wrapper
from agentic.llm import LLMClient
from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter

logger = structlog.get_logger()


class HTMLIngestor:
    """Ingest HTML documents with LLM-guided structure extraction."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        chunker: TokenAwareChunker,
        emitter: JSONLEmitter,
        llm_client: Optional[LLMClient] = None,
    ):
        """
        Initialize HTML ingestor.
        
        Args:
            config: Ingest configuration
            chunker: Token-aware chunker
            emitter: Output emitter
            llm_client: Optional LLM client for structure extraction
        """
        self.config = config
        self.chunker = chunker
        self.emitter = emitter
        self.llm = llm_client
        
        # Download settings
        self.timeout = config["download"]["timeout"]
        self.user_agent = config["download"]["user_agent"]
        self.min_content_length = config["html"]["min_content_length"]
        
        # LLM extractor settings
        self.llm_extractor_cfg = config.get("llm_html_extractor", {})
        self.llm_enabled = self.llm_extractor_cfg.get("enabled", False)
        self.max_chars = self.llm_extractor_cfg.get("max_chars", 120000)
        self.max_chars_llm = self.llm_extractor_cfg.get("max_chars_llm", 80000)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def download(self, url: str) -> tuple[str, Dict[str, str]]:
        """
        Download HTML content and headers.
        
        Returns:
            Tuple of (html_content, headers_dict)
        """
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text, dict(response.headers)
    
    def ingest(
        self,
        url: str,
        title: Optional[str],
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        expected_type: str = "html",
    ) -> Dict[str, Any]:
        """
        Ingest HTML document with LLM structure extraction.
        
        Returns:
            Dictionary with:
            - ok: bool
            - next_type: 'pdf' | 'html' | 'none'
            - next_url: str | None (PDF URL if wrapper detected)
        """
        # Validate expected type
        if expected_type and expected_type != "html":
            logger.error(
                "html_type_mismatch",
                url=url,
                expected=expected_type,
                executor="html",
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        try:
            # Step 1: Download HTML
            logger.info("html_download_start", url=url)
            html, response_headers = self.download(url)
            logger.info("html_downloaded", url=url, size=len(html))
            
            # Step 2: Check Content-Type
            content_type = response_headers.get("Content-Type", "").lower()
            if content_type and not any(ct in content_type for ct in ["html", "text/"]):
                logger.warning("html_wrong_content_type", url=url, content_type=content_type)
                return {"ok": False, "next_type": "none", "next_url": None}
            
            # Step 3: LLM extractor path (if enabled)
            if self.llm_enabled and self.llm:
                return self._ingest_with_llm(url, title, html, response_headers)
            else:
                # Fallback: readability-only
                return self._ingest_fallback(url, title, html)
        
        except requests.exceptions.RequestException as e:
            logger.error(
                "html_download_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        except Exception as e:
            logger.error(
                "html_ingest_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return {"ok": False, "next_type": "none", "next_url": None}
    
    def _ingest_with_llm(
        self,
        url: str,
        title: Optional[str],
        html: str,
        headers: Dict[str, str],
    ) -> Dict[str, Any]:
        """LLM-powered HTML ingestion with structure extraction."""
        
        # Check if PDF wrapper
        logger.info("html_pdf_wrapper_check", url=url)
        pdf_link = is_probably_pdf_wrapper(html, url)
        if pdf_link:
            logger.info("html_pdf_wrapper_detected", url=url, pdf_link=pdf_link)
            return {"ok": False, "next_type": "pdf", "next_url": pdf_link}
        
        # Extract clean excerpt with anchors
        logger.info("html_extract_start", url=url)
        bundle = clean_html_to_excerpt(html, url, self.max_chars)
        excerpt = bundle["excerpt"]
        pdf_links = bundle["pdf_links"]
        anchors_struct = bundle["anchors_struct"]
        
        logger.info(
            "html_extracted",
            url=url,
            excerpt_len=len(excerpt),
            pdf_links_count=len(pdf_links),
            anchors_count=len(anchors_struct),
        )
        
        # If strong PDF signal (many PDF links), consider routing to PDF
        if len(pdf_links) >= 3:
            logger.info("html_many_pdf_links", url=url, count=len(pdf_links))
            # Return first PDF link for routing
            return {"ok": False, "next_type": "pdf", "next_url": pdf_links[0]}
        
        # Check minimum content length
        if len(excerpt) < self.min_content_length:
            logger.warning(
                "html_content_too_short",
                url=url,
                length=len(excerpt),
                min_required=self.min_content_length,
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        # Call LLM to extract structure
        logger.info("html_llm_struct_start", url=url)
        doc = self.llm.extract_html_structure(url, excerpt, self.max_chars_llm)
        
        # Build content from sections
        if doc.get("sections"):
            content_parts = []
            for section in doc["sections"]:
                heading = section.get("heading", "")
                text = section.get("text", "")
                if heading:
                    content_parts.append(f"# {heading}")
                if text:
                    content_parts.append(text)
            content = "\n\n".join(content_parts)
        else:
            # Fallback to excerpt if no sections
            content = excerpt
        
        # Get anchors (prefer LLM anchors, fallback to struct anchors)
        anchors = doc.get("anchors") if doc.get("anchors") else anchors_struct
        
        logger.info(
            "html_llm_struct_done",
            url=url,
            sections_count=len(doc.get("sections", [])),
            anchors_count=len(anchors),
        )
        
        # Chunking with anchors
        logger.info("html_chunking_start", url=url)
        chunks = self.chunker.chunk(content, anchors=anchors)
        logger.info("html_chunked", url=url, num_chunks=len(chunks))
        
        # Emit chunks with metadata
        metadata = {
            "content_type": "text/html",
            "extracted_by": "llm+readability",
            "llm_model": self.llm_extractor_cfg.get("model"),
            "language": doc.get("language", "unknown"),
            "sections_count": len(doc.get("sections", [])),
        }
        
        logger.info("html_emit_start", url=url)
        self.emitter.emit_chunks(
            chunks=chunks,
            source_url=url,
            source_file="",
            anchors=anchors,
            metadata=metadata,
        )
        logger.info("html_ingest_complete", url=url)
        
        return {"ok": True, "next_type": "none", "next_url": None}
    
    def _ingest_fallback(
        self,
        url: str,
        title: Optional[str],
        html: str,
    ) -> Dict[str, Any]:
        """Fallback HTML ingestion without LLM (readability only)."""
        
        logger.info("html_extract_start", url=url)
        bundle = clean_html_to_excerpt(html, url, self.max_chars)
        content = bundle["excerpt"]
        anchors = bundle["anchors_struct"]
        
        logger.info("html_extracted", url=url, content_length=len(content))
        
        if len(content) < self.min_content_length:
            logger.warning(
                "html_content_too_short",
                url=url,
                length=len(content),
                min_required=self.min_content_length,
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        # Chunk content
        logger.info("html_chunking_start", url=url)
        chunks = self.chunker.chunk(content, anchors=anchors if anchors else None)
        logger.info("html_chunked", url=url, num_chunks=len(chunks))
        
        # Emit
        metadata = {
            "content_type": "text/html",
            "extracted_by": "readability",
        }
        
        logger.info("html_emit_start", url=url)
        self.emitter.emit_chunks(
            chunks=chunks,
            source_url=url,
            source_file="",
            anchors=anchors if anchors else None,
            metadata=metadata,
        )
        logger.info("html_ingest_complete", url=url)
        
        return {"ok": True, "next_type": "none", "next_url": None}

