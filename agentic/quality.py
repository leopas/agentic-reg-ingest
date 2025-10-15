# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Quality gates for agentic search candidate filtering."""

import re
from datetime import datetime, timedelta
from typing import List, Tuple

from agentic.schemas import CandidateSummary, QualityGates


def apply_quality_gates(
    gates: QualityGates,
    candidate: CandidateSummary,
) -> Tuple[bool, List[str]]:
    """
    Apply quality gates to a candidate.
    
    Args:
        gates: Quality gate configuration
        candidate: Candidate to evaluate
        
    Returns:
        Tuple of (approved: bool, violations: List[str])
    """
    violations = []
    
    # Gate 1: Document type must be in allowed list
    if candidate.final_type not in gates.must_types:
        violations.append(f"type:not_allowed (got '{candidate.final_type}', want {gates.must_types})")
    
    # Gate 2: Age check via Last-Modified header
    last_modified_str = candidate.headers.get("Last-Modified")
    if last_modified_str and gates.max_age_years > 0:
        try:
            # Parse Last-Modified header
            last_modified = datetime.strptime(
                last_modified_str,
                "%a, %d %b %Y %H:%M:%S %Z"
            )
            age_years = (datetime.utcnow() - last_modified).days / 365.25
            
            if age_years > gates.max_age_years:
                violations.append(f"age:stale ({age_years:.1f} years > {gates.max_age_years} years)")
        
        except Exception:
            # Failed to parse date, treat as warning but not blocking
            pass
    
    # Gate 3: Score threshold
    if candidate.score < gates.min_score:
        violations.append(f"score:low ({candidate.score:.2f} < {gates.min_score:.2f})")
    
    # Gate 4: Anchor signals (structural markers)
    if candidate.anchor_signals < gates.min_anchor_signals:
        violations.append(f"anchors:insufficient ({candidate.anchor_signals} < {gates.min_anchor_signals})")
    
    approved = len(violations) == 0
    
    return approved, violations


def count_anchor_signals(text: str) -> int:
    """
    Count structural/anchor signals in text (title, snippet, etc).
    
    Looks for:
    - Art. / Artigo
    - Anexo / ANEXO
    - Tabela / Table
    - Capítulo / CAPÍTULO
    - Heading tags (h1, h2, h3)
    
    Args:
        text: Text to analyze
        
    Returns:
        Count of anchor signals found
    """
    if not text:
        return 0
    
    text_lower = text.lower()
    count = 0
    
    # Regulatory markers
    patterns = [
        r'\bart\.\s*\d+',           # Art. 1, Art. 123
        r'\bartigo\s+\d+',          # Artigo 1
        r'\banexo\s+[ivxlcdm\d]+',  # Anexo I, Anexo 1
        r'\btabela\s+\d+',          # Tabela 1
        r'\bcap[íi]tulo\s+[ivxlcdm\d]+',  # Capítulo I
        r'\bseção\s+[ivxlcdm\d]+',  # Seção I
        r'\bparágrafo\s+\d+',       # Parágrafo 1
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        count += len(matches)
    
    # HTML heading tags (if present in snippet)
    heading_patterns = [
        r'<h[1-3]>',
        r'\bh1\b',
        r'\bh2\b',
        r'\bh3\b',
    ]
    
    for pattern in heading_patterns:
        matches = re.findall(pattern, text_lower)
        count += len(matches)
    
    return count

