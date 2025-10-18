# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Vertex AI Search provider implementation."""

from typing import List, Optional

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic.providers.base import (
    SearchProvider,
    SearchRequest,
    SearchResponse,
    SearchResult,
)

logger = structlog.get_logger()


class VertexProvider(SearchProvider):
    """
    Vertex AI Search (Discovery Engine) provider.
    
    Allow-list gerenciada via API:
    - Atualiza estado do índice
    - Não é dinâmico por chamada
    - Requer re-crawling para novos domínios
    """
    
    def __init__(
        self,
        project_id: str,
        datastore_id: str,
        location: str = "global",
        serving_config: str = "default_config",
        timeout: int = 30,
    ):
        """
        Initialize Vertex provider.
        
        Args:
            project_id: GCP Project ID
            datastore_id: Datastore ID
            location: Location (default: global)
            serving_config: Serving config name
            timeout: Request timeout
        """
        self.project_id = project_id
        self.datastore_id = datastore_id
        self.location = location
        self.serving_config = serving_config
        self.timeout = timeout
        
        try:
            from google.cloud import discoveryengine_v1 as discoveryengine
            
            self.client = discoveryengine.SearchServiceClient()
            
            # Build serving config path
            self.serving_config_path = self.client.serving_config_path(
                project=project_id,
                location=location,
                data_store=datastore_id,
                serving_config=serving_config,
            )
            
            logger.info(
                "vertex_provider_initialized",
                project=project_id,
                datastore=datastore_id,
            )
        
        except ImportError:
            logger.error("vertex_not_installed", msg="Install: pip install google-cloud-discoveryengine")
            self.client = None
            self.serving_config_path = None
        
        except Exception as e:
            logger.error("vertex_init_failed", error=str(e))
            self.client = None
            self.serving_config_path = None
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "vertex"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
    )
    def search(self, request: SearchRequest) -> SearchResponse:
        """
        Execute search.
        
        Note: include_domains/exclude_domains são usados como filtros,
        mas o datastore já deve ter esses domínios indexados.
        
        Args:
            request: Search request
            
        Returns:
            Search response
        """
        if not self.client or not self.serving_config_path:
            logger.error("vertex_not_available", msg="Client not initialized")
            return SearchResponse(
                results=[],
                total_results=0,
                page=request.page,
                page_size=request.page_size,
                provider="vertex",
            )
        
        logger.info(
            "vertex_search_start",
            query=request.q,
            include_domains=len(request.include_domains),
            page=request.page,
        )
        
        try:
            from google.cloud import discoveryengine_v1 as discoveryengine
            
            # Sanitize domains
            include_domains = self.sanitize_domains(request.include_domains)
            
            # Build filter expression
            filter_expr = self._build_filter(include_domains, request.exclude_domains)
            
            # Build request
            search_req = discoveryengine.SearchRequest(
                serving_config=self.serving_config_path,
                query=request.q,
                page_size=request.page_size,
                offset=(request.page - 1) * request.page_size,
            )
            
            if filter_expr:
                search_req.filter = filter_expr
            
            # Execute search
            response = self.client.search(request=search_req, timeout=self.timeout)
            
            # Parse results
            results = []
            for result in response.results:
                doc = result.document
                
                results.append(SearchResult(
                    url=doc.derived_struct_data.get("link", ""),
                    title=doc.derived_struct_data.get("title"),
                    snippet=self._extract_snippet(doc),
                    html_snippet=doc.derived_struct_data.get("htmlSnippet"),
                    metadata={
                        "id": doc.id,
                        "name": doc.name,
                    }
                ))
            
            logger.info("vertex_search_done", query=request.q, results=len(results))
            
            return SearchResponse(
                results=results,
                total_results=response.total_size if hasattr(response, 'total_size') else None,
                page=request.page,
                page_size=request.page_size,
                provider="vertex",
            )
        
        except Exception as e:
            logger.error("vertex_search_failed", query=request.q, error=str(e))
            raise
    
    def _build_filter(
        self,
        include_domains: List[str],
        exclude_domains: List[str],
    ) -> Optional[str]:
        """
        Build filter expression for Vertex AI Search.
        
        Format: uri: ANY("domain1.com", "domain2.com")
        
        Args:
            include_domains: Domains to include
            exclude_domains: Domains to exclude
            
        Returns:
            Filter expression or None
        """
        filters = []
        
        if include_domains:
            domains_str = ", ".join([f'"{d}"' for d in include_domains])
            filters.append(f"uri: ANY({domains_str})")
        
        # Note: exclude_domains would require NOT operator
        # Vertex AI Search filter syntax is limited
        
        return " AND ".join(filters) if filters else None
    
    def _extract_snippet(self, doc) -> Optional[str]:
        """Extract snippet from document."""
        try:
            snippets = doc.derived_struct_data.get("snippets", [])
            if snippets and len(snippets) > 0:
                return snippets[0].get("snippet", "")
        except Exception:
            pass
        
        return None
    
    def update_allowlist(self, include_domains: List[str]) -> bool:
        """
        Update datastore allowlist (add new domains).
        
        This triggers datastore update and re-crawling.
        
        Args:
            include_domains: Domains to add
            
        Returns:
            Success status
        """
        # TODO: Implement via Discovery Engine API
        # Requires:
        # 1. Get current website data source
        # 2. Add new domains to include_patterns
        # 3. Trigger re-index/re-crawl
        
        logger.warning(
            "vertex_update_allowlist_not_implemented",
            domains=len(include_domains),
            msg="Requires Discovery Engine DataStore API"
        )
        
        return False

