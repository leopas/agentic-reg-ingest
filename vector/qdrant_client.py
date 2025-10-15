# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Qdrant client helpers for vector operations."""

import os
import structlog
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

logger = structlog.get_logger()

# Environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")


def get_client() -> QdrantClient:
    """Get configured Qdrant client."""
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY or None,
        timeout=60.0,
    )


def ensure_collection(
    client: QdrantClient,
    collection: str,
    dim: int,
    distance: str = "Cosine",
) -> None:
    """
    Ensure collection exists, create if not.
    
    Args:
        client: Qdrant client
        collection: Collection name
        dim: Vector dimension
        distance: Distance metric (Cosine, Euclid, Dot)
    """
    existing = [c.name for c in client.get_collections().collections]
    
    if collection in existing:
        logger.info("qdrant_collection_exists", collection=collection)
        return
    
    logger.info("qdrant_creating_collection", collection=collection, dim=dim, distance=distance)
    
    # Map distance string to enum
    distance_map = {
        "Cosine": Distance.COSINE,
        "Euclid": Distance.EUCLID,
        "Euclidean": Distance.EUCLID,
        "Dot": Distance.DOT,
    }
    
    distance_enum = distance_map.get(distance, Distance.COSINE)
    
    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=dim, distance=distance_enum),
    )
    
    logger.info("qdrant_collection_created", collection=collection)


def delete_by_doc_hashes(
    client: QdrantClient,
    collection: str,
    doc_hashes: List[str],
) -> int:
    """
    Delete all points matching doc_hashes.
    
    Args:
        client: Qdrant client
        collection: Collection name
        doc_hashes: List of document hashes to delete
        
    Returns:
        Total number of points deleted
    """
    if not doc_hashes:
        return 0
    
    logger.info("qdrant_delete_start", collection=collection, hashes=len(doc_hashes))
    
    total_deleted = 0
    
    for doc_hash in doc_hashes:
        try:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="doc_hash",
                        match=MatchValue(value=doc_hash)
                    )
                ]
            )
            
            result = client.delete(
                collection_name=collection,
                points_selector=filter_condition,
                wait=True,
            )
            
            deleted = getattr(result, 'deleted', 0) or 0
            total_deleted += deleted
            
            logger.debug("qdrant_deleted_doc", doc_hash=doc_hash, deleted=deleted)
        
        except Exception as e:
            logger.error("qdrant_delete_failed", doc_hash=doc_hash, error=str(e))
    
    logger.info("qdrant_delete_done", total_deleted=total_deleted)
    
    return total_deleted


def upsert_points(
    client: QdrantClient,
    collection: str,
    points: List[PointStruct],
) -> int:
    """
    Upsert points to collection.
    
    Args:
        client: Qdrant client
        collection: Collection name
        points: List of points to upsert
        
    Returns:
        Number of points upserted
    """
    if not points:
        return 0
    
    logger.debug("qdrant_upsert", collection=collection, points=len(points))
    
    client.upsert(
        collection_name=collection,
        points=points,
        wait=True,
    )
    
    return len(points)

