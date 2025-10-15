# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Tests for PDF marker detection and anchoring."""

import pytest

from ingestion.anchors import AnchorDetector


@pytest.fixture
def sample_markers():
    """Sample markers for testing."""
    return [
        {"type": "article", "pattern": r"Art\. \d+", "confidence": 0.9},
        {"type": "chapter", "pattern": r"CAP[ÍI]TULO [IVX]+", "confidence": 0.8},
        {"type": "annex", "pattern": r"ANEXO [IVX]+", "confidence": 0.8},
    ]


@pytest.fixture
def detector(sample_markers):
    """Create AnchorDetector with sample markers."""
    return AnchorDetector(sample_markers)


def test_detect_articles(detector):
    """Test detection of article markers."""
    text = """
    Art. 1º - Define as regras gerais.
    Art. 2º - Estabelece critérios.
    Art. 3º - Dispõe sobre procedimentos.
    """
    
    anchors = detector.detect(text)
    
    # Should detect 3 articles
    article_anchors = [a for a in anchors if a["type"] == "article"]
    assert len(article_anchors) == 3


def test_detect_chapters(detector):
    """Test detection of chapter markers."""
    text = """
    CAPÍTULO I - Disposições Gerais
    CAPÍTULO II - Procedimentos
    CAPÍTULO III - Penalidades
    """
    
    anchors = detector.detect(text)
    
    # Should detect 3 chapters
    chapter_anchors = [a for a in anchors if a["type"] == "chapter"]
    assert len(chapter_anchors) == 3


def test_detect_annexes(detector):
    """Test detection of annex markers."""
    text = """
    ANEXO I - Tabela de Procedimentos
    ANEXO II - Formulários
    """
    
    anchors = detector.detect(text)
    
    # Should detect 2 annexes
    annex_anchors = [a for a in anchors if a["type"] == "annex"]
    assert len(annex_anchors) == 2


def test_segment_by_anchors(detector):
    """Test text segmentation by anchors."""
    text = """
    Art. 1º - Primeira regra com conteúdo extenso.
    Este artigo tem várias linhas de texto.
    
    Art. 2º - Segunda regra também extensa.
    Outro artigo com conteúdo.
    
    Art. 3º - Terceira regra.
    Mais conteúdo aqui.
    """
    
    segments = detector.segment_by_anchors(text, min_segment_length=10)
    
    # Should create segments for each article
    assert len(segments) >= 2  # At least 2 segments with min length


def test_segment_no_anchors(detector):
    """Test segmentation when no anchors found."""
    text = "Simple text without any markers."
    
    segments = detector.segment_by_anchors(text)
    
    # Should return whole text as one segment
    assert len(segments) == 1
    assert segments[0]["text"] == text
    assert segments[0]["anchor"] is None


def test_anchors_sorted_by_position(detector):
    """Test that detected anchors are sorted by position."""
    text = """
    CAPÍTULO I - Introduction
    Art. 1º - First rule
    Art. 2º - Second rule
    ANEXO I - Tables
    """
    
    anchors = detector.detect(text)
    
    # Verify anchors are in order of appearance
    for i in range(len(anchors) - 1):
        assert anchors[i]["start"] < anchors[i + 1]["start"]

