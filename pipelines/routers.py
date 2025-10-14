"""Intent routing for document types with DB-first strategy."""

import structlog
from typing import Any, Dict, Literal, Optional

import requests

from agentic.detect import detect_type
from agentic.llm import LLMClient

logger = structlog.get_logger()


class DocumentRouter:
    """Route documents to appropriate ingestor based on type."""
    
    def __init__(self, llm_client: LLMClient, timeout: int = 20):
        """
        Initialize router.
        
        Args:
            llm_client: LLM client for fallback routing
            timeout: HTTP request timeout
        """
        self.llm = llm_client
        self.timeout = timeout
    
    def route_item(
        self,
        url: str,
        content_type: Optional[str] = None,
        title: Optional[str] = None,
        snippet: Optional[str] = None,
        final_type: Optional[str] = None,
    ) -> Literal["pdf", "zip", "html", "unknown"]:
        """
        Route document to appropriate ingestor.
        
        Priority:
        1. Trust final_type from DB if in {pdf, zip, html}
        2. Re-detect live if unknown
        3. LLM fallback as last resort
        
        Args:
            url: Document URL
            content_type: Content-Type header (legacy)
            title: Document title
            snippet: Search snippet
            final_type: Pre-detected type from DB (pdf/zip/html/unknown)
            
        Returns:
            Document type: 'pdf', 'zip', 'html', or 'unknown'
        """
        # 1. Trust DB final_type if resolved
        if final_type and final_type in ("pdf", "zip", "html"):
            logger.debug("route_from_db", url=url, final_type=final_type)
            return final_type  # type: ignore
        
        # 2. Re-detect live if unknown or missing
        if final_type == "unknown" or not final_type:
            logger.debug("route_redetect", url=url)
            
            try:
                # HEAD request for headers
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                headers = dict(response.headers)
            except Exception as e:
                logger.warning("route_head_failed", url=url, error=str(e))
                headers = {}
            
            # Detect type
            typing_info = detect_type(url, headers, sniff_magic=True)
            detected = typing_info.get("final_type")
            
            if detected and detected in ("pdf", "zip", "html"):
                logger.info("route_redetected", url=url, final_type=detected)
                return detected  # type: ignore
        
        # 3. LLM fallback
        logger.debug("route_llm_fallback", url=url)
        llm_result = self.llm.route_fallback(
            title=title or "",
            snippet=snippet or "",
            url=url,
        )
        
        # Sanitize LLM output
        llm_result_clean = llm_result.strip().lower()
        
        if llm_result_clean in ("pdf", "zip", "html"):
            logger.info("route_from_llm", url=url, final_type=llm_result_clean)
            return llm_result_clean  # type: ignore
        else:
            logger.warning("route_llm_invalid", url=url, llm_output=llm_result)
            # Default to html for unknown (most common on web)
            return "html"

