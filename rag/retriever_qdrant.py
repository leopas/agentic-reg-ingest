# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Qdrant-based retriever for RAG."""

import os
import structlog
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchParams

logger = structlog.get_logger()

# Environment configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
DEFAULT_COLLECTION = os.getenv("RAG_COLLECTION", "kb_regulatory")


def get_client() -> QdrantClient:
    """Get configured Qdrant client."""
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY or None,
        timeout=60.0,
    )


def embed_query(query: str) -> List[float]:
    """
    Generate embedding for query.
    
    Args:
        query: Query text
        
    Returns:
        Embedding vector
    """
    from embeddings.encoder import encode_texts
    
    embeddings = encode_texts([query])
    return embeddings[0]


def search_collection(
    query: str,
    top_k: int = 8,
    collection: str = DEFAULT_COLLECTION,
    filter_must: Optional[List[Dict[str, Any]]] = None,
    score_threshold: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Search Qdrant collection with query.
    
    Args:
        query: Search query
        top_k: Number of results to return
        collection: Collection name
        filter_must: Optional filters (list of {"key": "...", "value": "..."})
        score_threshold: Minimum score threshold
        
    Returns:
        List of search results with payloads
    """
    logger.info("rag_search_start", query=query[:100], top_k=top_k, collection=collection)
    
    try:
        client = get_client()
        
        # Generate query embedding
        query_vector = embed_query(query)
        
        logger.debug("rag_embed_done", dim=len(query_vector))
        
        # Build filter if provided
        search_filter = None
        if filter_must:
            must_conditions = []
            for cond in filter_must:
                must_conditions.append(
                    FieldCondition(
                        key=cond["key"],
                        match=MatchValue(value=cond["value"])
                    )
                )
            search_filter = Filter(must=must_conditions)
        
        # Search
        results = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            search_params=SearchParams(hnsw_ef=128, exact=False),
        )
        
        logger.info("rag_search_done", results=len(results))
        
        # Format results
        items = []
        for r in results:
            payload = r.payload or {}
            
            item = {
                "id": r.id,
                "score": float(r.score),
                "text": payload.get("text", ""),
                "doc_hash": payload.get("doc_hash"),
                "chunk_id": payload.get("chunk_id"),
                "chunk_index": payload.get("chunk_index"),
                "url": payload.get("url") or payload.get("source_url"),
                "title": payload.get("title"),
                "source_type": payload.get("source_type"),
                "anchor_type": payload.get("anchor_type"),
                "anchor_text": payload.get("anchor_text"),
            }
            
            items.append(item)
        
        # Apply score threshold if provided
        if score_threshold is not None:
            items = [x for x in items if x["score"] >= score_threshold]
            logger.info("rag_filtered", remaining=len(items), threshold=score_threshold)
        
        return items
    
    except Exception as e:
        logger.error("rag_search_failed", error=str(e))
        raise

