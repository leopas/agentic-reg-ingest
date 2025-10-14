"""Tests for agentic quality gates."""

import pytest
from datetime import datetime, timedelta

from agentic.quality import apply_quality_gates, count_anchor_signals
from agentic.schemas import CandidateSummary, QualityGates


class TestCountAnchorSignals:
    """Test anchor signal counting."""
    
    def test_count_articles(self):
        """Test counting article markers."""
        text = "Art. 1 estabelece. Ver também Art. 23 e Artigo 45."
        count = count_anchor_signals(text)
        assert count >= 3
    
    def test_count_anexos(self):
        """Test counting annex markers."""
        text = "Conforme ANEXO I e Anexo II da resolução."
        count = count_anchor_signals(text)
        assert count >= 2
    
    def test_count_tables(self):
        """Test counting table markers."""
        text = "Ver Tabela 1 e Tabela 2 para detalhes."
        count = count_anchor_signals(text)
        assert count >= 2
    
    def test_count_chapters(self):
        """Test counting chapter markers."""
        text = "CAPÍTULO I - Disposições Gerais. Capítulo II - Normas."
        count = count_anchor_signals(text)
        assert count >= 2
    
    def test_no_signals(self):
        """Test text without anchor signals."""
        text = "Just some random text without markers."
        count = count_anchor_signals(text)
        assert count == 0


class TestApplyQualityGates:
    """Test quality gate application."""
    
    def test_all_gates_pass(self):
        """Test candidate passing all gates."""
        gates = QualityGates(
            must_types=["pdf", "zip"],
            max_age_years=3,
            min_anchor_signals=1,
            min_score=0.7,
        )
        
        # Fresh document
        last_modified = (datetime.utcnow() - timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        candidate = CandidateSummary(
            url="https://example.com/doc.pdf",
            title="RN 395 ANS",
            score=0.85,
            final_type="pdf",
            anchor_signals=3,
            headers={"Last-Modified": last_modified},
        )
        
        approved, violations = apply_quality_gates(gates, candidate)
        
        assert approved is True
        assert len(violations) == 0
    
    def test_wrong_type(self):
        """Test rejection due to wrong type."""
        gates = QualityGates(must_types=["pdf", "zip"])
        
        candidate = CandidateSummary(
            url="https://example.com/page.html",
            score=0.9,
            final_type="html",
            anchor_signals=5,
        )
        
        approved, violations = apply_quality_gates(gates, candidate)
        
        assert approved is False
        assert any("type:not_allowed" in v for v in violations)
    
    def test_stale_document(self):
        """Test rejection due to age."""
        gates = QualityGates(max_age_years=2)
        
        # 5 years old
        old_date = (datetime.utcnow() - timedelta(days=5*365)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        candidate = CandidateSummary(
            url="https://example.com/doc.pdf",
            score=0.9,
            final_type="pdf",
            anchor_signals=5,
            headers={"Last-Modified": old_date},
        )
        
        approved, violations = apply_quality_gates(gates, candidate)
        
        assert approved is False
        assert any("age:stale" in v for v in violations)
    
    def test_low_score(self):
        """Test rejection due to low score."""
        gates = QualityGates(min_score=0.8)
        
        candidate = CandidateSummary(
            url="https://example.com/doc.pdf",
            score=0.5,
            final_type="pdf",
            anchor_signals=5,
        )
        
        approved, violations = apply_quality_gates(gates, candidate)
        
        assert approved is False
        assert any("score:low" in v for v in violations)
    
    def test_insufficient_anchors(self):
        """Test rejection due to insufficient anchor signals."""
        gates = QualityGates(min_anchor_signals=3)
        
        candidate = CandidateSummary(
            url="https://example.com/doc.pdf",
            score=0.9,
            final_type="pdf",
            anchor_signals=1,  # Too few
        )
        
        approved, violations = apply_quality_gates(gates, candidate)
        
        assert approved is False
        assert any("anchors:insufficient" in v for v in violations)
    
    def test_multiple_violations(self):
        """Test candidate with multiple violations."""
        gates = QualityGates(
            must_types=["pdf"],
            min_score=0.8,
            min_anchor_signals=3,
        )
        
        candidate = CandidateSummary(
            url="https://example.com/page.html",
            score=0.5,
            final_type="html",
            anchor_signals=0,
        )
        
        approved, violations = apply_quality_gates(gates, candidate)
        
        assert approved is False
        assert len(violations) == 3  # type, score, anchors

