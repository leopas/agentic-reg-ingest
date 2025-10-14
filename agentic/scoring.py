"""Scoring and ranking for search results."""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from agentic.normalize import is_gov_domain


class ResultScorer:
    """Score search results based on multiple factors."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize scorer with configuration.
        
        Args:
            config: Configuration dict from cse.yaml
        """
        self.config = config
        self.authority_domains = config.get("authority_domains", [])
        self.specificity_keywords = config.get("specificity_keywords", {})
        self.type_preferences = config.get("type_preferences", {})
        self.anchor_markers = config.get("anchor_markers", [])
    
    def score(
        self,
        url: str,
        title: Optional[str],
        snippet: Optional[str],
        content_type: Optional[str],
        last_modified: Optional[datetime],
    ) -> float:
        """
        Compute composite score for a search result.
        
        Score components:
        - Authority (0.0-1.0): Government domains preferred
        - Freshness (0.0-1.0): Recent content preferred
        - Specificity (0.0-1.0): Regulatory keywords boost
        - Type boost (1.0-1.5): PDF > ZIP > HTML
        - Anchorability (0.0-0.2): Presence of structural markers
        
        Args:
            url: Document URL
            title: Document title
            snippet: Search snippet
            content_type: Content-Type header value
            last_modified: Last-Modified timestamp
            
        Returns:
            Composite score (0.0-5.0+)
        """
        authority = self._score_authority(url)
        freshness = self._score_freshness(last_modified)
        specificity = self._score_specificity(title, snippet, url)
        type_boost = self._score_type(content_type, url)
        anchorability = self._score_anchorability(snippet)
        
        # Weighted sum
        score = (
            authority * 1.0
            + freshness * 0.8
            + specificity * 1.2
            + type_boost
            + anchorability
        )
        
        return round(score, 4)
    
    def _score_authority(self, url: str) -> float:
        """Score based on domain authority."""
        domain = urlparse(url).netloc.lower()
        
        if is_gov_domain(domain):
            return 1.0
        
        # Check configured authority domains
        for auth_domain in self.authority_domains:
            if domain.endswith(auth_domain):
                return 1.0
        
        return 0.3
    
    def _score_freshness(self, last_modified: Optional[datetime]) -> float:
        """Score based on content freshness."""
        if not last_modified:
            return 0.5  # Unknown = medium score
        
        now = datetime.utcnow()
        age_days = (now - last_modified).days
        
        # Bucket by age
        if age_days < 30:
            return 1.0
        elif age_days < 90:
            return 0.9
        elif age_days < 180:
            return 0.8
        elif age_days < 365:
            return 0.6
        elif age_days < 730:
            return 0.4
        else:
            return 0.2
    
    def _score_specificity(
        self,
        title: Optional[str],
        snippet: Optional[str],
        url: str,
    ) -> float:
        """Score based on regulatory keyword presence."""
        text = " ".join(filter(None, [title or "", snippet or "", url]))
        text_lower = text.lower()
        
        score = 0.0
        
        # High value keywords
        for keyword in self.specificity_keywords.get("high", []):
            if keyword.lower() in text_lower:
                score += 0.4
        
        # Medium value keywords
        for keyword in self.specificity_keywords.get("medium", []):
            if keyword.lower() in text_lower:
                score += 0.2
        
        # Penalty for low-value keywords
        for keyword in self.specificity_keywords.get("low", []):
            if keyword.lower() in text_lower:
                score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _score_type(self, content_type: Optional[str], url: str) -> float:
        """Score based on content type preference."""
        # Infer from content-type header or URL extension
        type_str = ""
        
        if content_type:
            type_str = content_type.lower()
        else:
            url_lower = url.lower()
            if url_lower.endswith('.pdf'):
                type_str = 'pdf'
            elif url_lower.endswith('.zip'):
                type_str = 'zip'
            else:
                type_str = 'html'
        
        # Apply boost
        if 'pdf' in type_str:
            return self.type_preferences.get("pdf", 1.5)
        elif 'zip' in type_str:
            return self.type_preferences.get("zip", 1.3)
        else:
            return self.type_preferences.get("html", 1.0)
    
    def _score_anchorability(self, snippet: Optional[str]) -> float:
        """Score based on presence of structural markers."""
        if not snippet:
            return 0.0
        
        count = 0
        for marker in self.anchor_markers:
            if marker in snippet:
                count += 1
        
        # Max 0.2 boost
        return min(0.2, count * 0.05)

