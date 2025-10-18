# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Unified search API routes with provider selection."""

from typing import List, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic.providers import SearchRequest as ProviderSearchRequest
from agentic.search_service import get_search_service

logger = structlog.get_logger()

router = APIRouter()


class SearchRequest(BaseModel):
    """Search API request."""
    q: str = Field(..., min_length=1, description="Search query")
    include_domains: List[str] = Field(default_factory=list, description="Domains to include")
    exclude_domains: List[str] = Field(default_factory=list, description="Domains to exclude")
    provider: Optional[str] = Field(None, pattern="^(pse|vertex)$", description="Search provider")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Results per page")


class SearchResultItem(BaseModel):
    """Single search result."""
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    html_snippet: Optional[str] = None


class SearchAPIResponse(BaseModel):
    """Search API response."""
    results: List[SearchResultItem]
    total_results: Optional[int] = None
    page: int
    page_size: int
    provider: str
    cache_hit: bool = False


@router.post("/search", response_model=SearchAPIResponse)
async def unified_search(request: SearchRequest):
    """
    Unified search endpoint with provider selection.
    
    Supports:
    - PSE (Google Custom Search) - Dynamic allow-list per request
    - Vertex AI Search - Managed allow-list via API
    
    Features:
    - Cache (LRU in-memory + optional Redis)
    - Rate limiting and exponential backoff
    - Domain sanitization
    - Fallback to default provider
    
    Args:
        request: Search request with query and domains
        
    Returns:
        Search results with metadata
    """
    try:
        logger.info(
            "search_api_start",
            query=request.q,
            provider=request.provider or "default",
            include_domains=len(request.include_domains),
            exclude_domains=len(request.exclude_domains),
        )
        
        # Get search service
        service = get_search_service()
        
        # Convert to provider request
        provider_request = ProviderSearchRequest(
            q=request.q,
            include_domains=request.include_domains,
            exclude_domains=request.exclude_domains,
            page=request.page,
            page_size=request.page_size,
        )
        
        # Execute search
        response = service.search(
            request=provider_request,
            provider=request.provider,
            use_cache=True,
        )
        
        # Convert to API response
        results = [
            SearchResultItem(
                url=r.url,
                title=r.title,
                snippet=r.snippet,
                html_snippet=r.html_snippet,
            )
            for r in response.results
        ]
        
        logger.info(
            "search_api_done",
            query=request.q,
            provider=response.provider,
            results=len(results),
            cache_hit=response.cache_hit,
        )
        
        return SearchAPIResponse(
            results=results,
            total_results=response.total_results,
            page=response.page,
            page_size=response.page_size,
            provider=response.provider,
            cache_hit=response.cache_hit,
        )
    
    except ValueError as e:
        logger.error("search_api_validation_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error("search_api_failed", query=request.q, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/providers")
async def list_providers():
    """
    List available search providers.
    
    Returns:
        List of available providers and default
    """
    try:
        service = get_search_service()
        
        return {
            "providers": list(service.providers.keys()),
            "default": service.default_provider,
            "status": {
                provider: "available" for provider in service.providers.keys()
            }
        }
    
    except Exception as e:
        logger.error("search_providers_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

