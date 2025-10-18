# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Unified search service with caching and provider selection."""

import hashlib
import json
import os
from typing import Dict, Optional

import structlog

from agentic.providers import (
    PSEProvider,
    SearchProvider,
    SearchRequest,
    SearchResponse,
    VertexProvider,
)

logger = structlog.get_logger()


class SearchCache:
    """Simple LRU cache in memory (optional: extend to Redis)."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum cache entries
            ttl_seconds: Time to live for cache entries
        """
        self.cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[SearchResponse]:
        """Get from cache."""
        import time
        
        if key in self.cache:
            data, timestamp = self.cache[key]
            
            # Check TTL
            if time.time() - timestamp < self.ttl_seconds:
                logger.debug("cache_hit", key=key[:16])
                return SearchResponse(**data)
            else:
                # Expired
                del self.cache[key]
                logger.debug("cache_expired", key=key[:16])
        
        return None
    
    def set(self, key: str, value: SearchResponse):
        """Set in cache."""
        import time
        
        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size:
            # Simple eviction: remove first item (not true LRU, but good enough)
            first_key = next(iter(self.cache))
            del self.cache[first_key]
            logger.debug("cache_evicted", key=first_key[:16])
        
        self.cache[key] = (value.dict(), time.time())
        logger.debug("cache_set", key=key[:16])
    
    def build_key(self, request: SearchRequest, provider: str) -> str:
        """Build cache key from request."""
        key_str = json.dumps({
            "provider": provider,
            "q": request.q,
            "include": sorted(request.include_domains),
            "exclude": sorted(request.exclude_domains),
            "page": request.page,
            "page_size": request.page_size,
        }, sort_keys=True)
        
        return hashlib.sha256(key_str.encode()).hexdigest()


class SearchService:
    """Unified search service with provider selection and caching."""
    
    def __init__(self):
        """Initialize search service."""
        self.cache = SearchCache(
            max_size=int(os.getenv("SEARCH_CACHE_SIZE", "1000")),
            ttl_seconds=int(os.getenv("SEARCH_CACHE_TTL", "3600")),
        )
        
        # Initialize providers
        self.providers: Dict[str, SearchProvider] = {}
        
        # PSE Provider
        try:
            pse_api_key = os.getenv("GOOGLE_API_KEY", "")
            pse_cx = os.getenv("GOOGLE_CX", "")
            
            if pse_api_key and pse_cx:
                self.providers["pse"] = PSEProvider(
                    api_key=pse_api_key,
                    cx=pse_cx,
                    throttle_qps=float(os.getenv("PSE_THROTTLE_QPS", "1.0")),
                )
                logger.info("search_service_pse_available")
        except Exception as e:
            logger.warning("search_service_pse_init_failed", error=str(e))
        
        # Vertex Provider
        try:
            vertex_project = os.getenv("VERTEX_PROJECT_ID", "")
            vertex_datastore = os.getenv("VERTEX_DATASTORE_ID", "")
            
            if vertex_project and vertex_datastore:
                self.providers["vertex"] = VertexProvider(
                    project_id=vertex_project,
                    datastore_id=vertex_datastore,
                    location=os.getenv("VERTEX_LOCATION", "global"),
                )
                logger.info("search_service_vertex_available")
        except Exception as e:
            logger.warning("search_service_vertex_init_failed", error=str(e))
        
        # Default provider
        self.default_provider = os.getenv("SEARCH_ENGINE", "pse")
        
        logger.info(
            "search_service_initialized",
            providers=list(self.providers.keys()),
            default=self.default_provider,
        )
    
    def search(
        self,
        request: SearchRequest,
        provider: Optional[str] = None,
        use_cache: bool = True,
    ) -> SearchResponse:
        """
        Execute search with caching and provider selection.
        
        Args:
            request: Search request
            provider: Provider name (pse, vertex) or None for default
            use_cache: Enable caching
            
        Returns:
            Search response
        """
        # Select provider
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            logger.warning(
                "search_provider_not_available",
                requested=provider_name,
                available=list(self.providers.keys()),
                msg="Falling back to first available"
            )
            if self.providers:
                provider_name = list(self.providers.keys())[0]
            else:
                raise ValueError("No search providers available")
        
        search_provider = self.providers[provider_name]
        
        # Check cache
        if use_cache:
            cache_key = self.cache.build_key(request, provider_name)
            cached_response = self.cache.get(cache_key)
            
            if cached_response:
                cached_response.cache_hit = True
                logger.info("search_cache_hit", provider=provider_name)
                return cached_response
        
        # Execute search
        logger.info(
            "search_service_execute",
            provider=provider_name,
            query=request.q,
            include_domains=len(request.include_domains),
        )
        
        response = search_provider.search(request)
        
        # Cache response
        if use_cache:
            self.cache.set(cache_key, response)
        
        return response


# Global service instance
_service_instance = None


def get_search_service() -> SearchService:
    """Get or create global search service instance."""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = SearchService()
    
    return _service_instance

