# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""HTML extraction utilities with readability and PDF wrapper detection."""

import re
import structlog
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import trafilatura
from bs4 import BeautifulSoup

logger = structlog.get_logger()


def clean_html_to_excerpt(html: str, base_url: str, max_chars: int) -> Dict:
    """
    Extract clean text excerpt from HTML with anchors and PDF links.
    
    Args:
        html: Raw HTML content
        base_url: Base URL for resolving relative links
        max_chars: Maximum characters to return
        
    Returns:
        Dictionary with:
        - excerpt: Clean text content
        - pdf_links: List of absolute PDF URLs found
        - anchors_struct: List of heading/table anchors
    """
    result = {
        "excerpt": "",
        "pdf_links": [],
        "anchors_struct": [],
    }
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script, style, noscript tags
        for tag in soup(['script', 'style', 'noscript', 'meta', 'link']):
            tag.decompose()
        
        # Collect PDF links
        pdf_links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # Check if likely PDF
            if href.lower().endswith('.pdf') or '.pdf?' in href.lower():
                pdf_links.add(absolute_url)
            elif 'pdf' in href.lower() and urlparse(href).path.endswith('.pdf'):
                pdf_links.add(absolute_url)
        
        result["pdf_links"] = sorted(list(pdf_links))
        
        # Collect heading anchors
        anchors = []
        for level in range(1, 5):  # h1, h2, h3, h4
            for heading in soup.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                if text:
                    anchors.append({
                        "type": f"h{level}",
                        "value": text[:200],  # Truncate very long headings
                    })
        
        # Collect table markers
        for table in soup.find_all('table'):
            # Try to find caption or first row header
            caption = table.find('caption')
            if caption:
                caption_text = caption.get_text(strip=True)
            else:
                # Try first row
                first_row = table.find('tr')
                if first_row:
                    headers = first_row.find_all(['th', 'td'])
                    caption_text = ' | '.join([h.get_text(strip=True) for h in headers[:3]])
                else:
                    caption_text = "Table"
            
            if caption_text:
                anchors.append({
                    "type": "table",
                    "value": caption_text[:200],
                })
        
        result["anchors_struct"] = anchors
        
        # Extract clean text using trafilatura
        try:
            # Try trafilatura first (best for article extraction)
            extracted = trafilatura.extract(
                html,
                output_format='xml',
                include_tables=True,
                include_links=False,
                include_images=False,
            )
            
            if extracted:
                # Parse XML output to get text
                xml_soup = BeautifulSoup(extracted, 'lxml-xml')
                text = xml_soup.get_text(separator='\n', strip=True)
            else:
                # Fallback to soup
                text = soup.get_text(separator='\n', strip=True)
        
        except Exception as e:
            logger.warning("trafilatura_failed", error=str(e))
            # Fallback to BeautifulSoup
            text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines -> double
        text = re.sub(r' +', ' ', text)  # Multiple spaces -> single
        
        # Truncate to max_chars
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        result["excerpt"] = text
        
        logger.debug(
            "html_excerpt_extracted",
            url=base_url,
            excerpt_len=len(text),
            pdf_links_count=len(pdf_links),
            anchors_count=len(anchors),
        )
        
    except Exception as e:
        logger.error("html_extract_failed", url=base_url, error=str(e))
        result["excerpt"] = html[:max_chars] if html else ""
    
    return result


def is_probably_pdf_wrapper(html: str, base_url: str) -> Optional[str]:
    """
    Detect if HTML is a PDF wrapper/redirect page.
    
    Args:
        html: Raw HTML content
        base_url: Base URL
        
    Returns:
        Absolute URL of PDF if detected, else None
    """
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Check for iframe/embed pointing to PDF
        for tag in soup.find_all(['iframe', 'embed', 'object']):
            src = tag.get('src') or tag.get('data')
            if src:
                absolute_url = urljoin(base_url, src)
                if src.lower().endswith('.pdf') or '.pdf?' in src.lower():
                    logger.info("pdf_wrapper_iframe_detected", url=base_url, pdf=absolute_url)
                    return absolute_url
        
        # Check for meta refresh to PDF
        for meta in soup.find_all('meta', attrs={'http-equiv': re.compile('refresh', re.I)}):
            content = meta.get('content', '')
            # Format: "0;URL=http://example.com/file.pdf"
            match = re.search(r'url\s*=\s*["\']?([^"\'>\s]+)', content, re.I)
            if match:
                url = match.group(1)
                absolute_url = urljoin(base_url, url)
                if url.lower().endswith('.pdf') or '.pdf?' in url.lower():
                    logger.info("pdf_wrapper_meta_detected", url=base_url, pdf=absolute_url)
                    return absolute_url
        
        # Check for dominant PDF link (main content is just a download link)
        body_text = soup.body.get_text(strip=True) if soup.body else ""
        if len(body_text) < 500:  # Very short page
            # Look for prominent PDF link
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf') or '.pdf?' in href.lower():
                    link_text = link.get_text(strip=True).lower()
                    # Keywords indicating it's a download page
                    if any(kw in link_text for kw in ['download', 'baixar', 'pdf', 'documento', 'arquivo']):
                        absolute_url = urljoin(base_url, href)
                        logger.info("pdf_wrapper_link_detected", url=base_url, pdf=absolute_url)
                        return absolute_url
        
        return None
        
    except Exception as e:
        logger.error("pdf_wrapper_detection_failed", url=base_url, error=str(e))
        return None

