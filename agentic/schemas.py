# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Pydantic schemas for Agentic Search system."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class QuerySpec(BaseModel):
    """Single query specification."""
    q: str = Field(..., description="Query string")
    why: Optional[str] = Field("Query relevante ao objetivo", description="Rationale for this query")
    k: int = Field(10, ge=1, le=10, description="Desired results per query")


class StopConditions(BaseModel):
    """Loop termination conditions."""
    min_approved: int = Field(12, ge=1, description="Minimum approved documents to collect")
    max_iterations: int = Field(3, ge=1, le=10, description="Maximum loop iterations")
    max_queries_per_iter: int = Field(2, ge=1, le=5, description="Max queries to execute per iteration")


class QualityGates(BaseModel):
    """Quality criteria for candidate approval."""
    must_types: List[str] = Field(["pdf", "zip"], description="Allowed final_type values")
    max_age_years: int = Field(3, ge=0, description="Maximum document age in years")
    min_anchor_signals: int = Field(1, ge=0, description="Minimum anchor/structure signals")
    min_score: float = Field(0.65, ge=0.0, le=5.0, description="Minimum scoring threshold (0-5 scale)")


class Budget(BaseModel):
    """Resource budget constraints."""
    max_cse_calls: int = Field(60, ge=1, description="Maximum CSE API calls")
    ttl_days: int = Field(7, ge=1, description="Cache TTL in days")


class Plan(BaseModel):
    """Agentic search plan."""
    goal: str = Field(..., description="Search objective")
    topics: List[str] = Field(default_factory=list, description="Topic areas")
    queries: List[QuerySpec] = Field(..., min_items=1, description="Query specifications")
    allow_domains: List[str] = Field(default_factory=list, description="Whitelist domains")
    deny_patterns: List[str] = Field(default_factory=list, description="Blacklist regex patterns")
    stop: StopConditions = Field(default_factory=StopConditions, description="Stop conditions")
    quality_gates: QualityGates = Field(default_factory=QualityGates, description="Quality criteria")
    budget: Budget = Field(default_factory=Budget, description="Resource budget")


class CandidateSummary(BaseModel):
    """Summary of a search result candidate."""
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    headers: dict = Field(default_factory=dict, description="HTTP headers")
    score: float = Field(0.0, ge=0.0, le=5.0, description="Composite score (0-5, weighted sum)")
    final_type: str = Field("unknown", description="Detected document type")
    anchor_signals: int = Field(0, ge=0, description="Count of structural signals")


class RejectedSummary(BaseModel):
    """Summary of a rejected candidate."""
    url: str
    reason: str
    violations: List[str] = Field(default_factory=list, description="Quality gate violations")


class IterationResult(BaseModel):
    """Result of one agentic loop iteration."""
    iteration: int
    executed_queries: List[str]
    candidates: List[CandidateSummary]
    approved: List[CandidateSummary]
    rejected: List[RejectedSummary]
    new_queries: List[str]
    reason_to_continue: Optional[str] = None


class JudgeResponse(BaseModel):
    """LLM judge response."""
    approved_urls: List[str] = Field(default_factory=list)
    rejected: List[RejectedSummary] = Field(default_factory=list)
    new_queries: List[str] = Field(default_factory=list)


class AgenticResult(BaseModel):
    """Final result of agentic search."""
    plan_id: str
    iterations: int
    approved_total: int
    stopped_by: str = Field(..., description="Reason for stopping: min_approved|max_iterations|budget|no_progress")
    promoted_urls: List[str]
    summary: Optional[str] = None

