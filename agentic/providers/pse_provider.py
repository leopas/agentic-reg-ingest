# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""PSE (Programmable Search Engine) provider implementation."""

import time
from typing import List, Optional

import requests
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from agentic.providers.base import (
    SearchProvider,
    SearchRequest,
    SearchResponse,
    SearchResult,
)

logger = structlog.get_logger()


class PSEProvider(SearchProvider):
    """
    Google Programmable Search Engine (PSE) provider.
    
    Allow-list dinâmico por requisição usando:
    - site: operator (e.g., "query site:arxiv.org OR site:openai.com")
    - siteSearch parameter (deprecated mas ainda funciona)
    """
    
    def __init__(
        self,
        api_key: str,
        cx: str,
        timeout: int = 30,
        throttle_qps: float = 1.0,
    ):
        """
        Initialize PSE provider.
        
        Args:
            api_key: Google API key
            cx: Custom Search Engine ID
            timeout: Request timeout
            throttle_qps: Queries per second throttle (default: 1.0)
        """
        self.api_key = api_key
        self.cx = cx
        self.timeout = timeout
        self.throttle_delay = 1.0 / throttle_qps if throttle_qps > 0 else 0
        self.last_call_time = 0
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "pse"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.HTTPError)),
    )
    def search(self, request: SearchRequest) -> SearchResponse:
        """
        Execute search with dynamic allow-list.
        
        PSE permite allow-list dinâmico via:
        1. site: operator na query (recomendado)
        2. siteSearch parameter (deprecated)
        
        Args:
            request: Search request
            
        Returns:
            Search response
        """
        logger.info(
            "pse_search_start",
            query=request.q,
            include_domains=len(request.include_domains),
            exclude_domains=len(request.exclude_domains),
            page=request.page,
        )
        
        # Throttle requests
        self._throttle()
        
        # Sanitize domains
        include_domains = self.sanitize_domains(request.include_domains)
        exclude_domains = self.sanitize_domains(request.exclude_domains)
        
        # Build query with site: operators
        query = self._build_query_with_domains(
            request.q,
            include_domains,
            exclude_domains,
        )
        
        # Calculate start index for pagination
        start_index = ((request.page - 1) * request.page_size) + 1
        
        # Build request params
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "start": start_index,
            "num": min(request.page_size, 10),  # Max 10 per request
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse results
            results = []
            items = data.get("items", [])
            
            for item in items:
                results.append(SearchResult(
                    url=item.get("link", ""),
                    title=item.get("title"),
                    snippet=item.get("snippet"),
                    html_snippet=item.get("htmlSnippet"),
                    metadata={
                        "display_link": item.get("displayLink"),
                        "formatted_url": item.get("formattedUrl"),
                    }
                ))
            
            total_results = int(data.get("searchInformation", {}).get("totalResults", 0))
            
            logger.info("pse_search_done", query=request.q, results=len(results))
            
            return SearchResponse(
                results=results,
                total_results=total_results,
                page=request.page,
                page_size=request.page_size,
                provider="pse",
                cache_hit=False,
            )
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("pse_rate_limited", msg="Rate limit hit, retrying...")
                raise  # Retry will handle it
            else:
                logger.error("pse_http_error", status=e.response.status_code, error=str(e))
                raise
        
        except Exception as e:
            logger.error("pse_search_failed", query=request.q, error=str(e))
            raise
    
    def _build_query_with_domains(
        self,
        query: str,
        include_domains: List[str],
        exclude_domains: List[str],
    ) -> str:
        """
        Build query with site: operators.
        
        Include domains: site:arxiv.org OR site:openai.com
        Exclude domains: -site:spam.com
        
        Args:
            query: Base query
            include_domains: Domains to include
            exclude_domains: Domains to exclude
            
        Returns:
            Modified query string
        """
        parts = [query]
        
        # Add include domains (OR logic)
        if include_domains:
            site_clauses = [f"site:{d}" for d in include_domains]
            include_expr = "(" + " OR ".join(site_clauses) + ")"
            parts.append(include_expr)
        
        # Add exclude domains
        if exclude_domains:
            for domain in exclude_domains:
                parts.append(f"-site:{domain}")
        
        final_query = " ".join(parts)
        
        logger.debug("pse_query_built", original=query, final=final_query)
        
        return final_query
    
    def _throttle(self):
        """Throttle requests to respect QPS limit."""
        if self.throttle_delay > 0:
            now = time.time()
            elapsed = now - self.last_call_time
            
            if elapsed < self.throttle_delay:
                sleep_time = self.throttle_delay - elapsed
                logger.debug("pse_throttle_sleep", seconds=sleep_time)
                time.sleep(sleep_time)
            
            self.last_call_time = time.time()

