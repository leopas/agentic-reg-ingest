"""Robust document type detection with magic bytes, headers, and URL analysis."""

import re
import structlog
from typing import Dict, Optional
from urllib.parse import urlparse

import requests

logger = structlog.get_logger()


def _url_ext(url: str) -> Optional[str]:
    """
    Extract file extension from URL path.
    
    Args:
        url: URL to analyze
        
    Returns:
        Extension without dot ('pdf', 'zip', 'html', 'htm') or None
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Remove query params and fragments
        path = path.split('?')[0].split('#')[0]
        
        # Get extension
        if '.' in path:
            ext = path.rsplit('.', 1)[1]
            # Known extensions
            if ext in ('pdf', 'zip', 'html', 'htm', 'csv', 'txt', 'xlsx', 'xls'):
                return ext
        
        return None
    except Exception:
        return None


def _sniff_magic(url: str, timeout: int = 20) -> Optional[bytes]:
    """
    Fetch first 8 bytes via Range GET to detect magic bytes.
    
    Args:
        url: URL to sniff
        timeout: Request timeout in seconds
        
    Returns:
        First 8 bytes or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RegulatoryBot/1.0)',
            'Range': 'bytes=0-7',
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        
        # Accept 200 (full response) or 206 (partial content)
        if response.status_code in (200, 206):
            # Read first 8 bytes
            chunk = next(response.iter_content(chunk_size=8), b'')
            response.close()
            return chunk[:8]
        
        return None
        
    except Exception as e:
        logger.debug("magic_sniff_failed", url=url, error=str(e))
        return None


def _detect_from_magic(magic: bytes) -> Optional[str]:
    """
    Detect file type from magic bytes.
    
    Args:
        magic: First bytes of file
        
    Returns:
        'pdf', 'zip', or None
    """
    if not magic or len(magic) < 4:
        return None
    
    # PDF: %PDF- (25 50 44 46 2D)
    if magic.startswith(b'%PDF-'):
        return 'pdf'
    
    # ZIP: PK signatures
    # PK\x03\x04 (normal zip)
    # PK\x05\x06 (empty zip)
    # PK\x07\x08 (spanned zip)
    if magic.startswith(b'PK\x03\x04') or \
       magic.startswith(b'PK\x05\x06') or \
       magic.startswith(b'PK\x07\x08'):
        return 'zip'
    
    return None


def _detect_from_disposition(disposition: Optional[str]) -> Optional[str]:
    """
    Detect file type from Content-Disposition filename.
    
    Args:
        disposition: Content-Disposition header value
        
    Returns:
        'pdf', 'zip', 'html', or None
    """
    if not disposition:
        return None
    
    # Extract filename from Content-Disposition
    # Example: attachment; filename="document.pdf"
    # Example: inline; filename*=UTF-8''file%20name.zip
    
    filename_match = re.search(r'filename[*]?=["\']?([^"\';\s]+)', disposition, re.IGNORECASE)
    if filename_match:
        filename = filename_match.group(1).lower()
        
        # Decode URL-encoded filenames
        try:
            from urllib.parse import unquote
            filename = unquote(filename)
        except Exception:
            pass
        
        # Check extension
        if filename.endswith('.pdf'):
            return 'pdf'
        elif filename.endswith('.zip'):
            return 'zip'
        elif filename.endswith(('.html', '.htm')):
            return 'html'
    
    return None


def _detect_from_content_type(content_type: Optional[str], url_extension: Optional[str]) -> Optional[str]:
    """
    Detect file type from Content-Type header.
    
    Args:
        content_type: Content-Type header value
        url_extension: URL extension for disambiguation
        
    Returns:
        'pdf', 'zip', 'html', or None
    """
    if not content_type:
        return None
    
    content_type_lower = content_type.lower()
    
    # PDF
    if 'pdf' in content_type_lower or 'application/pdf' in content_type_lower:
        return 'pdf'
    
    # ZIP
    if 'zip' in content_type_lower or \
       'application/zip' in content_type_lower or \
       'application/x-zip-compressed' in content_type_lower:
        return 'zip'
    
    # HTML
    if 'html' in content_type_lower or 'text/html' in content_type_lower:
        # But check URL extension - if URL says .pdf, trust that over Content-Type
        if url_extension == 'pdf':
            return 'pdf'
        elif url_extension == 'zip':
            return 'zip'
        return 'html'
    
    # Text (could be HTML without proper MIME)
    if 'text/' in content_type_lower:
        # Check URL extension for clarification
        if url_extension in ('html', 'htm'):
            return 'html'
        elif url_extension == 'pdf':
            return 'pdf'
        # Default text to HTML
        return 'html'
    
    return None


def detect_type(url: str, head_headers: Dict[str, str], sniff_magic: bool = True) -> Dict[str, Optional[str]]:
    """
    Detect document type using multiple signals.
    
    Detection order (first match wins):
    1. Magic bytes (if sniff_magic=True)
    2. Content-Disposition filename
    3. Content-Type header (with URL extension disambiguation)
    4. URL extension
    5. Fallback: 'unknown'
    
    Args:
        url: Document URL
        head_headers: Headers from HEAD request (dict with Content-Type, Content-Disposition, etc.)
        sniff_magic: Whether to fetch magic bytes via Range GET
        
    Returns:
        Dictionary with:
        - detected_mime: MIME type from headers or magic
        - detected_ext: Extension from detection
        - final_type: 'pdf' | 'zip' | 'html' | 'unknown'
        - fetch_status: 'ok' | 'redirected' | 'blocked' | 'error'
    """
    result = {
        "detected_mime": None,
        "detected_ext": None,
        "final_type": "unknown",
        "fetch_status": "ok",
    }
    
    # Extract signals
    content_type = head_headers.get('Content-Type') or head_headers.get('content-type')
    content_disposition = head_headers.get('Content-Disposition') or head_headers.get('content-disposition')
    url_extension = _url_ext(url)
    
    detected_type = None
    detection_source = None
    
    try:
        # 1. Magic bytes (highest priority)
        if sniff_magic:
            magic = _sniff_magic(url)
            if magic:
                magic_type = _detect_from_magic(magic)
                if magic_type:
                    detected_type = magic_type
                    detection_source = "magic"
                    result["detected_mime"] = f"application/{magic_type}" if magic_type in ('pdf', 'zip') else None
                    result["detected_ext"] = magic_type
        
        # 2. Content-Disposition filename
        if not detected_type:
            disp_type = _detect_from_disposition(content_disposition)
            if disp_type:
                detected_type = disp_type
                detection_source = "disposition"
                result["detected_ext"] = disp_type
        
        # 3. Content-Type header
        if not detected_type:
            ctype_result = _detect_from_content_type(content_type, url_extension)
            if ctype_result:
                detected_type = ctype_result
                detection_source = "content_type"
                result["detected_mime"] = content_type
        
        # 4. URL extension
        if not detected_type and url_extension:
            if url_extension in ('pdf', 'zip'):
                detected_type = url_extension
                detection_source = "url_ext"
                result["detected_ext"] = url_extension
            elif url_extension in ('html', 'htm'):
                detected_type = 'html'
                detection_source = "url_ext"
                result["detected_ext"] = url_extension
        
        # Set final type
        if detected_type:
            result["final_type"] = detected_type
            logger.debug(
                "type_detected",
                url=url,
                final_type=detected_type,
                source=detection_source,
            )
        else:
            result["final_type"] = "unknown"
            logger.debug("type_unknown", url=url)
        
    except Exception as e:
        logger.error("detection_error", url=url, error=str(e))
        result["fetch_status"] = "error"
    
    return result

