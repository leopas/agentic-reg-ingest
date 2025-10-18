# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Pydantic schemas for vision enrichment pipeline."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PageOCR(BaseModel):
    """OCR result for a single page."""
    page: int
    text: str
    confidence: Optional[float] = None


class BBox(BaseModel):
    """Bounding box for a figure."""
    x: float
    y: float
    width: float
    height: float


class FigureInfo(BaseModel):
    """Information about a figure/image in a document."""
    caption: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    bbox: Optional[BBox] = None
    confidence: Optional[float] = None


class EvidenceSpan(BaseModel):
    """Text span evidence for an inference."""
    start: int
    end: int
    text: str


class GuidedInference(BaseModel):
    """Guided inference from multimodal analysis."""
    hypothesis: str
    rationale: str
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    section_hint: Optional[str] = None


class DocumentJSONL(BaseModel):
    """Single line in output JSONL."""
    doc_id: str
    page: int
    text: str
    figures: List[FigureInfo] = Field(default_factory=list)
    guided_inferences: List[GuidedInference] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class QuerySpec(BaseModel):
    """Query with justification."""
    q: str
    why: str


class AllowlistPlan(BaseModel):
    """Allowlist plan from GPT."""
    goal: str
    allow_domains: List[str]
    queries: List[QuerySpec]
    stop: Dict[str, Any]
    quality_gates: Dict[str, Any]


class UploadJobResponse(BaseModel):
    """Response for upload endpoint."""
    upload_id: str
    status: str
    message: str


class PipelineStatusResponse(BaseModel):
    """Response for status endpoint."""
    upload_id: str
    status: str
    stage_ocr: str
    stage_multimodal: str
    stage_allowlist: str
    stage_agentic: str
    stage_scrape: str
    stage_vector: str
    jsonl_path: Optional[str] = None
    txt_output_dir: Optional[str] = None
    plan_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class VectorPushRequest(BaseModel):
    """Request to push to vector DB."""
    upload_id: str
    collection: Optional[str] = "kb_regulatory"
    overwrite: bool = False

