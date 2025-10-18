# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Web scraper with HTML normalization to text."""

import hashlib
from datetime import datetime, timezone
from typing import Dict, Optional
from urllib.parse import urlparse

import requests
import structlog
from bs4 import BeautifulSoup

logger = structlog.get_logger()


class WebScraper:
    """Simple web scraper with text normalization."""
    
    def __init__(self, timeout: int = 20, user_agent: Optional[str] = None):
        """
        Initialize scraper.
        
        Args:
            timeout: HTTP timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; AgenticRegIngest/2.0; +https://github.com/user/repo)"
        )
    
    def scrape(self, url: str) -> Dict:
        """
        Scrape URL and normalize to text.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict with:
                - ok: bool (success flag)
                - url: str (original URL)
                - domain: str
                - fetched_at: str (ISO8601)
                - text: str (normalized text)
                - doc_hash: str (SHA256 of text)
                - error: str (if failed)
        """
        logger.info("scraper_start", url=url)
        
        try:
            # Fetch content
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
            )
            
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("Content-Type", "")
            
            if "text/html" not in content_type.lower():
                logger.warning("scraper_not_html", url=url, content_type=content_type)
                # Still try to parse
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Normalize to text
            normalized_text = self._normalize_html_to_text(soup)
            
            # Compute hash
            doc_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
            
            # Extract domain
            domain = urlparse(url).netloc
            
            logger.info("scraper_done", url=url, text_len=len(normalized_text), doc_hash=doc_hash[:16])
            
            return {
                "ok": True,
                "url": url,
                "domain": domain,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "text": normalized_text,
                "doc_hash": doc_hash,
            }
        
        except requests.exceptions.RequestException as e:
            logger.error("scraper_http_failed", url=url, error=str(e))
            return {
                "ok": False,
                "url": url,
                "error": f"HTTP error: {str(e)}",
            }
        
        except Exception as e:
            logger.error("scraper_failed", url=url, error=str(e))
            return {
                "ok": False,
                "url": url,
                "error": str(e),
            }
    
    def _normalize_html_to_text(self, soup: BeautifulSoup) -> str:
        """
        Normalize HTML to clean text.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Normalized text with headers preserved
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract text with structure
        lines = []
        
        # Process headings and paragraphs
        for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "div"]):
            text = element.get_text(strip=True)
            
            if not text:
                continue
            
            # Format headings
            if element.name in ["h1", "h2", "h3"]:
                lines.append(f"\n{text.upper()}\n")
            elif element.name in ["h4", "h5", "h6"]:
                lines.append(f"\n{text}\n")
            else:
                lines.append(text)
        
        # Join and clean
        normalized = "\n".join(lines)
        
        # Remove excessive whitespace
        normalized = "\n".join(
            line.strip() for line in normalized.split("\n") if line.strip()
        )
        
        return normalized

