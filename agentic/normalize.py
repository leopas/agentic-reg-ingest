# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""URL normalization utilities."""

from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """
    Normalize URL to canonical form.
    
    - Remove fragments (#)
    - Remove trailing slashes
    - Lowercase scheme and netloc
    - Keep query parameters
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL
    """
    parsed = urlparse(url)
    
    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip('/') if parsed.path != '/' else parsed.path
    params = parsed.params
    query = parsed.query
    # Remove fragment
    fragment = ''
    
    normalized = urlunparse((scheme, netloc, path, params, query, fragment))
    return normalized


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain (netloc)
    """
    parsed = urlparse(url)
    return parsed.netloc.lower()


def is_gov_domain(domain: str) -> bool:
    """
    Check if domain is a government domain.
    
    Args:
        domain: Domain string
        
    Returns:
        True if government domain
    """
    gov_tlds = ['.gov.br', 'ans.gov.br', 'saude.gov.br', 'planalto.gov.br', 'in.gov.br']
    return any(domain.endswith(tld) for tld in gov_tlds)

