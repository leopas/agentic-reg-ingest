# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Tests for scoring module."""

from datetime import datetime, timedelta

import pytest

from agentic.scoring import ResultScorer


@pytest.fixture
def scorer_config():
    """Mock CSE config for scorer."""
    return {
        "authority_domains": [".gov.br", "ans.gov.br"],
        "specificity_keywords": {
            "high": ["RN 259", "TISS", "TUSS"],
            "medium": ["Regulamentação"],
            "low": ["Notícia"],
        },
        "type_preferences": {
            "pdf": 1.5,
            "zip": 1.3,
            "html": 1.0,
        },
        "anchor_markers": ["Art.", "Anexo", "Tabela"],
    }


@pytest.fixture
def scorer(scorer_config):
    """Create ResultScorer instance."""
    return ResultScorer(scorer_config)


def test_score_authority_gov_domain(scorer):
    """Test authority scoring for government domains."""
    score = scorer._score_authority("https://ans.gov.br/documento.pdf")
    assert score == 1.0


def test_score_authority_non_gov(scorer):
    """Test authority scoring for non-government domains."""
    score = scorer._score_authority("https://example.com/documento.pdf")
    assert score == 0.3


def test_score_freshness_recent(scorer):
    """Test freshness scoring for recent content."""
    last_modified = datetime.utcnow() - timedelta(days=15)
    score = scorer._score_freshness(last_modified)
    assert score == 1.0


def test_score_freshness_old(scorer):
    """Test freshness scoring for old content."""
    last_modified = datetime.utcnow() - timedelta(days=800)
    score = scorer._score_freshness(last_modified)
    assert score == 0.2


def test_score_freshness_unknown(scorer):
    """Test freshness scoring for unknown date."""
    score = scorer._score_freshness(None)
    assert score == 0.5


def test_score_specificity_high_keywords(scorer):
    """Test specificity with high-value keywords."""
    score = scorer._score_specificity(
        title="RN 259 - Tabela TUSS",
        snippet="Resolução normativa sobre procedimentos",
        url="https://ans.gov.br/rn259.pdf",
    )
    assert score > 0.5


def test_score_specificity_low_keywords(scorer):
    """Test specificity with low-value keywords."""
    score = scorer._score_specificity(
        title="Notícia sobre saúde",
        snippet="Blog com artigos",
        url="https://example.com",
    )
    assert score < 0.5


def test_score_type_pdf(scorer):
    """Test type scoring for PDF."""
    score = scorer._score_type("application/pdf", "doc.pdf")
    assert score == 1.5


def test_score_type_zip(scorer):
    """Test type scoring for ZIP."""
    score = scorer._score_type("application/zip", "doc.zip")
    assert score == 1.3


def test_score_type_html(scorer):
    """Test type scoring for HTML."""
    score = scorer._score_type("text/html", "page.html")
    assert score == 1.0


def test_score_anchorability(scorer):
    """Test anchorability scoring."""
    snippet = "Art. 1º - Define regras. Ver Anexo I e Tabela 2."
    score = scorer._score_anchorability(snippet)
    assert score > 0


def test_score_composite(scorer):
    """Test full composite scoring."""
    score = scorer.score(
        url="https://ans.gov.br/rn259.pdf",
        title="RN 259 - TISS",
        snippet="Art. 1º - Define padrão TISS. Ver Anexo I.",
        content_type="application/pdf",
        last_modified=datetime.utcnow() - timedelta(days=20),
    )
    
    # Should be high score for gov PDF with regulatory keywords
    assert score > 3.0

