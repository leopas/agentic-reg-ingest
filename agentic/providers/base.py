# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Base search provider interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SearchRequest(BaseModel):
    """Search request parameters."""
    q: str
    include_domains: List[str] = []
    exclude_domains: List[str] = []
    page: int = 1
    page_size: int = 10


class SearchResult(BaseModel):
    """Single search result."""
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    html_snippet: Optional[str] = None
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseModel):
    """Search response."""
    results: List[SearchResult]
    total_results: Optional[int] = None
    page: int
    page_size: int
    provider: str
    cache_hit: bool = False


class SearchProvider(ABC):
    """Abstract base class for search providers."""
    
    @abstractmethod
    def search(self, request: SearchRequest) -> SearchResponse:
        """
        Execute search.
        
        Args:
            request: Search request parameters
            
        Returns:
            Search response with results
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name (pse, vertex, etc.)."""
        pass
    
    def sanitize_domains(self, domains: List[str]) -> List[str]:
        """
        Sanitize domain list.
        
        Args:
            domains: Raw domain list
            
        Returns:
            Sanitized domain list
        """
        sanitized = []
        
        for domain in domains:
            # Remove protocol
            domain = domain.replace("https://", "").replace("http://", "")
            
            # Remove trailing slash
            domain = domain.rstrip("/")
            
            # Remove www. prefix (optional, depends on use case)
            # domain = domain.replace("www.", "")
            
            # Basic validation
            if domain and "." in domain and len(domain) > 3:
                sanitized.append(domain.lower().strip())
        
        return list(set(sanitized))  # Deduplicate

