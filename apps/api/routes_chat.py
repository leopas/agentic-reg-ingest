# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Chat RAG API routes."""

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

logger = structlog.get_logger()

router = APIRouter()


class ChatAskRequest(BaseModel):
    """Request for chat RAG."""
    question: str = Field(..., min_length=2, description="User question")
    mode: str = Field("grounded", pattern="^(grounded|infer)$", description="Response mode")
    top_k: int = Field(8, ge=1, le=20, description="Number of chunks to retrieve")
    score_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum similarity score")
    collection: Optional[str] = Field("kb_regulatory", description="Qdrant collection name")


class ChunkLog(BaseModel):
    """Chunk log entry."""
    doc_hash: Optional[str] = None
    chunk_id: Optional[str] = None
    score: float
    title: Optional[str] = None
    url: Optional[str] = None
    source_type: Optional[str] = None
    anchor_type: Optional[str] = None


class ChatAskResponse(BaseModel):
    """Response for chat RAG."""
    answer: str
    used: List[ChunkLog]
    log: List[ChunkLog]


@router.post("/chat/ask", response_model=ChatAskResponse)
async def chat_ask(request: ChatAskRequest):
    """
    Ask question to RAG system.
    
    Two modes:
    - grounded: Answer only based on retrieved chunks (no extrapolation)
    - infer: Allow reasoning over chunks (with explicit inference markers)
    
    Returns:
        Answer with logs of chunks considered
    """
    try:
        logger.info("chat_ask_start", question=request.question[:100], mode=request.mode)
        
        from rag.answerer import run_rag
        
        # Run RAG pipeline
        result = run_rag(
            question=request.question,
            mode=request.mode,
            top_k=min(max(request.top_k, 1), 20),
            score_threshold=request.score_threshold,
            collection=request.collection,
        )
        
        logger.info("chat_ask_done", answer_len=len(result["answer"]), chunks_used=len(result["used"]))
        
        return ChatAskResponse(
            answer=result["answer"],
            used=[ChunkLog(**chunk) for chunk in result["used"]],
            log=[ChunkLog(**chunk) for chunk in result["log"]],
        )
    
    except Exception as e:
        logger.error("chat_ask_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

