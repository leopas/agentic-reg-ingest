# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Vertex AI Search (Discovery Engine) client wrapper."""

import os
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


class VertexSearchClient:
    """
    Wrapper for Google Vertex AI Search (Discovery Engine API).
    
    Vantagens sobre CSE:
    - CRUD de allowlist dinâmico
    - Datastore customizável
    - Melhor ranking e personalização
    - Suporta unstructured data (websites, PDFs)
    """
    
    def __init__(
        self,
        project_id: str,
        location: str = "global",
        datastore_id: Optional[str] = None,
        serving_config: str = "default_config",
        timeout: int = 30,
    ):
        """
        Initialize Vertex AI Search client.
        
        Args:
            project_id: GCP Project ID
            location: Location (default: global)
            datastore_id: Datastore ID (unstructured data store)
            serving_config: Serving config name
            timeout: Request timeout
        """
        self.project_id = project_id
        self.location = location
        self.datastore_id = datastore_id
        self.serving_config = serving_config
        self.timeout = timeout
        
        try:
            from google.cloud import discoveryengine_v1 as discoveryengine
            
            self.client = discoveryengine.SearchServiceClient()
            
            # Build serving config path
            if datastore_id:
                self.serving_config_path = self.client.serving_config_path(
                    project=project_id,
                    location=location,
                    data_store=datastore_id,
                    serving_config=serving_config,
                )
            else:
                self.serving_config_path = None
            
            logger.info(
                "vertex_search_initialized",
                project=project_id,
                datastore=datastore_id,
                location=location
            )
        
        except ImportError:
            logger.error("vertex_search_not_installed", msg="Install: pip install google-cloud-discoveryengine")
            self.client = None
            self.serving_config_path = None
        
        except Exception as e:
            logger.error("vertex_search_init_failed", error=str(e))
            self.client = None
            self.serving_config_path = None
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        filter_expr: Optional[str] = None,
        boost_spec: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search using Vertex AI Search.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            filter_expr: Filter expression (e.g., "uri: ANY(\"arxiv.org\")")
            boost_spec: Boost specification for ranking
            
        Returns:
            List of search results
        """
        if not self.client or not self.serving_config_path:
            logger.error("vertex_search_not_available", msg="Client not initialized")
            return []
        
        try:
            from google.cloud import discoveryengine_v1 as discoveryengine
            
            logger.info("vertex_search_query", query=query, max_results=max_results)
            
            # Build request
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config_path,
                query=query,
                page_size=max_results,
            )
            
            # Add filter if provided
            if filter_expr:
                request.filter = filter_expr
            
            # Add boost spec if provided
            if boost_spec:
                request.boost_spec = boost_spec
            
            # Execute search
            response = self.client.search(request=request, timeout=self.timeout)
            
            # Parse results
            results = []
            for result in response.results:
                doc = result.document
                
                # Extract data from document
                data = {
                    "link": doc.derived_struct_data.get("link", ""),
                    "title": doc.derived_struct_data.get("title", ""),
                    "snippet": doc.derived_struct_data.get("snippets", [{"snippet": ""}])[0].get("snippet", ""),
                    "htmlSnippet": doc.derived_struct_data.get("htmlSnippet", ""),
                }
                
                results.append(data)
            
            logger.info("vertex_search_done", query=query, results=len(results))
            
            return results
        
        except Exception as e:
            logger.error("vertex_search_failed", query=query, error=str(e))
            return []
    
    def search_all(
        self,
        query: str,
        max_results: int = 100,
        allow_domains: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search with pagination and domain filtering.
        
        Args:
            query: Search query
            max_results: Maximum total results
            allow_domains: List of allowed domains
            
        Returns:
            List of all search results
        """
        # Build filter expression for domains
        filter_expr = None
        if allow_domains:
            # Build OR filter: uri: ANY("domain1.com", "domain2.com")
            domains_str = ", ".join([f'"{d}"' for d in allow_domains])
            filter_expr = f"uri: ANY({domains_str})"
            
            logger.info("vertex_search_filter", domains=len(allow_domains), filter=filter_expr)
        
        return self.search(
            query=query,
            max_results=max_results,
            filter_expr=filter_expr,
        )
    
    def update_allowlist(self, domains: List[str]) -> bool:
        """
        Update datastore allowlist dynamically.
        
        This would require configuring the datastore with website data sources.
        
        Args:
            domains: List of domains to add to allowlist
            
        Returns:
            Success status
        """
        # TODO: Implement datastore update via Discovery Engine API
        # This requires:
        # 1. Create/update website data source
        # 2. Add domains to inclusion patterns
        # 3. Trigger re-indexing
        
        logger.warning(
            "vertex_allowlist_update_not_implemented",
            domains=len(domains),
            msg="Requires Discovery Engine datastore configuration"
        )
        
        return False

