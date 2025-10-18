# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Google Custom Search Engine (CSE) client."""

from typing import Any, Dict, List, Optional

import requests
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()


class CSEClient:
    """Client for Google Programmable Search Engine API."""
    
    def __init__(self, api_key: str, cx: str, timeout: int = 30):
        """
        Initialize CSE client.
        
        Args:
            api_key: Google API key
            cx: Custom Search Engine ID
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.cx = cx
        self.timeout = timeout
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def search(
        self,
        query: str,
        start: int = 1,
        num: int = 10,
        language: str = "lang_pt",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute search query.
        
        Args:
            query: Search query string
            start: Start index (1-based)
            num: Number of results per page (max 10)
            language: Language restriction
            **kwargs: Additional CSE API parameters
            
        Returns:
            API response dictionary
            
        Raises:
            requests.RequestException: On API errors
        """
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "start": start,
            "num": num,
            "lr": language,
            **kwargs,
        }
        
        response = requests.get(
            self.base_url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        
        return response.json()
    
    def search_all(
        self,
        query: str,
        max_results: int = 100,
        results_per_page: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute paginated search to collect multiple results.
        
        Suporta allow-list dinâmico por requisição usando site: operators.
        
        Args:
            query: Search query string
            max_results: Maximum total results to retrieve
            results_per_page: Results per API call (max 10)
            include_domains: Domains to include (dynamic allow-list)
            exclude_domains: Domains to exclude
            **kwargs: Additional CSE API parameters
            
        Returns:
            List of search result items
        """
        # ✅ Build query with dynamic allow-list
        final_query = self._build_query_with_allowlist(
            query,
            include_domains or [],
            exclude_domains or [],
        )
        
        all_items = []
        start = 1
        
        while len(all_items) < max_results:
            try:
                response = self.search(
                    query=final_query,  # ← Query modificada com site: operators
                    start=start,
                    num=min(results_per_page, 10),
                    **kwargs,
                )
                
                items = response.get("items", [])
                if not items:
                    break
                
                all_items.extend(items)
                
                # Check if more results available
                search_info = response.get("searchInformation", {})
                total_results = int(search_info.get("totalResults", 0))
                
                if len(all_items) >= total_results:
                    break
                
                start += len(items)
                
            except requests.RequestException:
                # Stop on error
                break
        
        return all_items[:max_results]
    
    def _build_query_with_allowlist(
        self,
        query: str,
        include_domains: List[str],
        exclude_domains: List[str],
    ) -> str:
        """
        Build query with site: operators for dynamic allow-list.
        
        PSE permite allow-list dinâmico POR REQUISIÇÃO usando site: operator.
        Não altera configuração do motor, apenas modifica a query.
        
        Args:
            query: Base query
            include_domains: Domains to include
            exclude_domains: Domains to exclude
            
        Returns:
            Modified query string
        """
        parts = [query]
        
        # ✅ Include domains (OR logic)
        if include_domains:
            site_clauses = [f"site:{d}" for d in include_domains]
            include_expr = "(" + " OR ".join(site_clauses) + ")"
            parts.append(include_expr)
        
        # ✅ Exclude domains
        if exclude_domains:
            for domain in exclude_domains:
                parts.append(f"-site:{domain}")
        
        final_query = " ".join(parts)
        
        if include_domains or exclude_domains:
            logger.info(
                "cse_allowlist_dynamic",
                original_query=query,
                final_query=final_query,
                include_domains=len(include_domains),
                exclude_domains=len(exclude_domains),
            )
        
        return final_query

