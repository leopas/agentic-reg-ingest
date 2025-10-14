"""Tests for agentic search plan schema."""

import pytest
from pydantic import ValidationError

from agentic.schemas import (
    Plan,
    QuerySpec,
    StopConditions,
    QualityGates,
    Budget,
    CandidateSummary,
    RejectedSummary,
)


class TestPlanSchema:
    """Test Plan schema validation."""
    
    def test_minimal_plan(self):
        """Test minimal valid plan."""
        plan = Plan(
            goal="Test goal",
            queries=[QuerySpec(q="test query", k=5)],
        )
        
        assert plan.goal == "Test goal"
        assert len(plan.queries) == 1
        assert plan.queries[0].q == "test query"
        assert plan.queries[0].k == 5
    
    def test_full_plan(self):
        """Test full plan with all fields."""
        plan_dict = {
            "goal": "Buscar RNs ANS sobre prazos",
            "topics": ["prazos", "atendimento"],
            "queries": [
                {"q": "RN ANS prazos", "why": "Main query", "k": 10},
                {"q": "Resolução Normativa prazos máximos", "k": 5},
            ],
            "allow_domains": ["www.gov.br/ans"],
            "deny_patterns": [".*blog.*"],
            "stop": {
                "min_approved": 15,
                "max_iterations": 4,
                "max_queries_per_iter": 3,
            },
            "quality_gates": {
                "must_types": ["pdf"],
                "max_age_years": 2,
                "min_anchor_signals": 2,
                "min_score": 0.75,
            },
            "budget": {
                "max_cse_calls": 100,
                "ttl_days": 14,
            },
        }
        
        plan = Plan(**plan_dict)
        
        assert plan.goal == "Buscar RNs ANS sobre prazos"
        assert len(plan.topics) == 2
        assert len(plan.queries) == 2
        assert plan.stop.min_approved == 15
        assert plan.quality_gates.must_types == ["pdf"]
        assert plan.budget.max_cse_calls == 100
    
    def test_plan_without_queries_fails(self):
        """Test that plan requires at least one query."""
        with pytest.raises(ValidationError):
            Plan(
                goal="Test",
                queries=[],  # Empty queries
            )
    
    def test_query_k_validation(self):
        """Test that k is validated (1-10)."""
        # k too high
        with pytest.raises(ValidationError):
            QuerySpec(q="test", k=20)
        
        # k too low
        with pytest.raises(ValidationError):
            QuerySpec(q="test", k=0)
        
        # Valid k
        query = QuerySpec(q="test", k=5)
        assert query.k == 5
    
    def test_default_values(self):
        """Test default values are applied."""
        plan = Plan(
            goal="Test",
            queries=[QuerySpec(q="test", k=5)],
        )
        
        # Defaults should be set
        assert plan.topics == []
        assert plan.allow_domains == []
        assert plan.deny_patterns == []
        assert plan.stop.min_approved == 12
        assert plan.stop.max_iterations == 3
        assert plan.quality_gates.must_types == ["pdf", "zip"]
        assert plan.quality_gates.min_score == 0.65


class TestCandidateSummary:
    """Test CandidateSummary schema."""
    
    def test_minimal_candidate(self):
        """Test minimal candidate."""
        candidate = CandidateSummary(
            url="https://example.com/doc.pdf",
        )
        
        assert candidate.url == "https://example.com/doc.pdf"
        assert candidate.score == 0.0
        assert candidate.final_type == "unknown"
        assert candidate.anchor_signals == 0
    
    def test_full_candidate(self):
        """Test full candidate."""
        candidate = CandidateSummary(
            url="https://example.com/doc.pdf",
            title="RN 395 ANS",
            snippet="Art. 1 estabelece...",
            headers={"Content-Type": "application/pdf"},
            score=0.95,
            final_type="pdf",
            anchor_signals=5,
        )
        
        assert candidate.title == "RN 395 ANS"
        assert candidate.final_type == "pdf"
        assert candidate.anchor_signals == 5
        assert candidate.score == 0.95


class TestRejectedSummary:
    """Test RejectedSummary schema."""
    
    def test_rejected_with_violations(self):
        """Test rejected summary."""
        rejected = RejectedSummary(
            url="https://example.com/old.pdf",
            reason="Documento desatualizado",
            violations=["age:stale", "score:low"],
        )
        
        assert rejected.url == "https://example.com/old.pdf"
        assert rejected.reason == "Documento desatualizado"
        assert len(rejected.violations) == 2

