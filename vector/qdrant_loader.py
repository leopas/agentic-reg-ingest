# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Load JSONL chunks into Qdrant vector database."""

import argparse
import json
import structlog
from pathlib import Path
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from common.env_readers import load_yaml_with_env

logger = structlog.get_logger()


class QdrantLoader:
    """Load document chunks into Qdrant."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Qdrant loader.
        
        Args:
            config: Configuration from settings.yaml
        """
        self.config = config
        
        # Initialize client
        url = config["url"]
        api_key = config.get("api_key", "")
        
        self.client = QdrantClient(url=url, api_key=api_key if api_key else None)
        
        self.collection_name = config["collection"]["name"]
        self.vector_size = config["collection"]["vector_size"]
        self.distance = self._get_distance_metric(config["collection"]["distance"])
        self.batch_size = config.get("batch_size", 100)
    
    def _get_distance_metric(self, distance_str: str) -> Distance:
        """Convert distance string to Qdrant Distance enum."""
        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclidean": Distance.EUCLID,
            "Dot": Distance.DOT,
        }
        return distance_map.get(distance_str, Distance.COSINE)
    
    def ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            logger.info("creating_collection", name=self.collection_name)
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance,
                ),
            )
        else:
            logger.info("collection_exists", name=self.collection_name)
    
    def load_jsonl(self, jsonl_path: Path) -> List[Dict[str, Any]]:
        """
        Load chunks from JSONL file.
        
        Args:
            jsonl_path: Path to JSONL file
            
        Returns:
            List of chunk records
        """
        chunks = []
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        For production, use sentence-transformers or OpenAI embeddings.
        This is a placeholder that returns a zero vector.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        # TODO: Replace with actual embedding model
        # Example with sentence-transformers:
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer(self.config["collection"]["embedding_model"])
        # return model.encode(text).tolist()
        
        # Placeholder: return zero vector
        return [0.0] * self.vector_size
    
    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Upsert chunks into Qdrant.
        
        Args:
            chunks: List of chunk records from JSONL
        """
        logger.info("upserting_chunks", count=len(chunks))
        
        points = []
        
        for idx, chunk in enumerate(chunks):
            # Generate embedding
            text = chunk["text"]
            embedding = self.generate_embedding(text)
            
            # Create point
            point = PointStruct(
                id=idx,  # In production, use UUID or hash
                vector=embedding,
                payload={
                    "text": text,
                    "source_url": chunk.get("source_url", ""),
                    "source_file": chunk.get("source_file", ""),
                    "chunk_index": chunk.get("chunk_index", 0),
                    "total_chunks": chunk.get("total_chunks", 1),
                    "anchor_type": chunk.get("anchor_type"),
                    "anchor_text": chunk.get("anchor_text"),
                },
            )
            
            points.append(point)
            
            # Batch upsert
            if len(points) >= self.batch_size:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
                points = []
        
        # Upsert remaining
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
        
        logger.info("upsert_complete")
    
    def load_from_file(self, jsonl_path: Path) -> None:
        """
        Load chunks from JSONL file into Qdrant.
        
        Args:
            jsonl_path: Path to JSONL file
        """
        # Ensure collection exists
        self.ensure_collection()
        
        # Load chunks
        chunks = self.load_jsonl(jsonl_path)
        logger.info("loaded_chunks", count=len(chunks))
        
        # Upsert
        self.upsert_chunks(chunks)
    
    def delete_by_doc_hashes(self, doc_hashes: List[str], collection: str | None = None) -> int:
        """
        Delete all points from VectorDB that match the given doc_hashes.
        
        Args:
            doc_hashes: List of document hashes to delete
            collection: Collection name (uses default if not provided)
            
        Returns:
            Number of points deleted
        """
        collection_name = collection or self.collection_name
        
        logger.info("vector_delete_start", doc_hashes=len(doc_hashes), collection=collection_name)
        
        try:
            # Delete points by filtering on doc_hash in payload
            from qdrant_client.models import Filter, FieldCondition, MatchAny
            
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="doc_hash",
                        match=MatchAny(any=doc_hashes)
                    )
                ]
            )
            
            # Scroll to get point IDs first
            points_to_delete = []
            scroll_result = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=filter_condition,
                limit=1000,
                with_payload=False,
                with_vectors=False,
            )
            
            while scroll_result[0]:
                points_to_delete.extend([p.id for p in scroll_result[0]])
                
                # Check if there are more results
                if scroll_result[1] is None:
                    break
                    
                scroll_result = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=filter_condition,
                    limit=1000,
                    offset=scroll_result[1],
                    with_payload=False,
                    with_vectors=False,
                )
            
            # Delete by IDs
            if points_to_delete:
                self.client.delete(
                    collection_name=collection_name,
                    points_selector=points_to_delete,
                )
            
            deleted_count = len(points_to_delete)
            logger.info("vector_delete_done", deleted=deleted_count)
            
            return deleted_count
        
        except Exception as e:
            logger.error("vector_delete_failed", error=str(e))
            return 0
    
    def exists_by_doc_hash(self, doc_hashes: List[str], collection: str | None = None) -> Dict[str, bool]:
        """
        Check which doc_hashes exist in VectorDB.
        
        Args:
            doc_hashes: List of document hashes to check
            collection: Collection name (uses default if not provided)
            
        Returns:
            Dict mapping doc_hash to existence boolean
        """
        collection_name = collection or self.collection_name
        result = {h: False for h in doc_hashes}
        
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchAny
            
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="doc_hash",
                        match=MatchAny(any=doc_hashes)
                    )
                ]
            )
            
            # Scroll to get unique doc_hashes
            scroll_result = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=filter_condition,
                limit=1000,
                with_payload=["doc_hash"],
                with_vectors=False,
            )
            
            found_hashes = set()
            while scroll_result[0]:
                for point in scroll_result[0]:
                    if point.payload and "doc_hash" in point.payload:
                        found_hashes.add(point.payload["doc_hash"])
                
                if scroll_result[1] is None:
                    break
                    
                scroll_result = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=filter_condition,
                    limit=1000,
                    offset=scroll_result[1],
                    with_payload=["doc_hash"],
                    with_vectors=False,
                )
            
            # Update result dict
            for h in found_hashes:
                if h in result:
                    result[h] = True
            
            return result
        
        except Exception as e:
            logger.error("vector_exists_failed", error=str(e))
            return result


def push_doc_hashes(
    doc_hashes: List[str],
    collection: str,
    batch_size: int = 64,
    overwrite: bool = False,
    fetch_chunks_fn=None,
    fetch_manifests_fn=None,
    mark_manifest_vector_fn=None,
) -> Dict[str, Any]:
    """
    Push chunks to VectorDB for specified doc_hashes.
    
    Args:
        doc_hashes: List of document hashes to push
        collection: Collection name
        batch_size: Batch size for upsert operations
        overwrite: If True, delete existing points first
        fetch_chunks_fn: Function to fetch chunks by hashes
        fetch_manifests_fn: Function to fetch manifests by hashes
        mark_manifest_vector_fn: Function to update manifest vector status
        
    Returns:
        Dictionary with pushed, skipped counts and per-doc details
    """
    from datetime import datetime
    from qdrant_client.models import PointStruct
    from vector.qdrant_client import (
        delete_by_doc_hashes,
        ensure_collection,
        get_client,
        upsert_points,
    )
    from embeddings.encoder import encode_texts, get_embedding_dim
    
    logger.info("push_start", doc_hashes=len(doc_hashes), collection=collection, overwrite=overwrite)
    
    # Fetch data
    chunks_by_hash = fetch_chunks_fn(doc_hashes) if fetch_chunks_fn else {}
    manifests = fetch_manifests_fn(doc_hashes) if fetch_manifests_fn else {}
    
    # Get embedding dimension
    dim = get_embedding_dim()
    
    # Ensure collection exists
    client = get_client()
    ensure_collection(client, collection, dim=dim, distance="Cosine")
    
    # Overwrite: delete existing points
    if overwrite:
        deleted = delete_by_doc_hashes(client, collection, doc_hashes)
        logger.info("push_overwrite_deleted", deleted=deleted)
    
    # Process each doc_hash
    pushed_total = 0
    per_doc = {}
    
    for doc_hash in doc_hashes:
        all_chunks = chunks_by_hash.get(doc_hash) or []
        
        if not all_chunks:
            per_doc[doc_hash] = {"pushed": 0, "chunks": 0, "status": "no_chunks"}
            continue
        
        pushed_doc = 0
        
        # Process in batches
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            
            # Prepare common payload
            common_payload = {
                "collection": collection,
                "pushed_at": datetime.utcnow().isoformat(),
            }
            
            # Enrich with manifest data
            manifest = manifests.get(doc_hash) or {}
            if manifest:
                common_payload.update({
                    "title": manifest.get("title"),
                    "source_type": manifest.get("source_type"),
                    "url": manifest.get("url_norm"),
                })
            
            # Normalize chunk data
            for j, chunk in enumerate(batch):
                chunk.setdefault("doc_hash", doc_hash)
                # Ensure chunk_id is just the index (not doc_hash:index)
                if "chunk_id" not in chunk:
                    chunk["chunk_id"] = str(i + j)
            
            # Generate embeddings
            texts = [c["text"] for c in batch]
            
            try:
                vectors = encode_texts(texts)
            except Exception as e:
                logger.error("push_encode_failed", doc_hash=doc_hash, error=str(e))
                per_doc[doc_hash] = {"pushed": 0, "chunks": len(all_chunks), "status": "encode_error", "error": str(e)}
                continue
            
            # Create points
            points = []
            for chunk, vector in zip(batch, vectors):
                chunk_idx = chunk.get("chunk_index", 0)
                
                payload = dict(common_payload)
                payload.update({
                    "doc_hash": chunk["doc_hash"],
                    "chunk_id": str(chunk.get("chunk_id", "0")),
                    "chunk_index": chunk_idx,
                    "source_type": chunk.get("metadata", {}).get("source_type"),
                    "text_len": len(chunk["text"]),
                    "tokens": chunk.get("tokens"),
                    "text": chunk["text"],  # Store full text for retrieval
                })
                
                # Add anchor info if present
                anchors = chunk.get("anchors")
                if anchors:
                    if isinstance(anchors, dict):
                        payload["anchor_type"] = anchors.get("type")
                        payload["anchor_text"] = anchors.get("value")
                
                # Point ID: Qdrant requires unsigned integer or UUID
                # Generate deterministic integer from doc_hash + chunk_index
                # Create deterministic ID: hash(doc_hash + chunk_index) as unsigned int
                import hashlib
                id_string = f"{chunk['doc_hash']}:{chunk_idx}"
                id_hash = hashlib.sha256(id_string.encode()).hexdigest()
                # Take first 16 hex chars and convert to int (64-bit safe)
                point_id = int(id_hash[:16], 16)
                
                # Store readable ID in payload for debugging
                payload["point_id_readable"] = id_string
                
                points.append(PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                ))
            
            # Upsert batch
            try:
                upserted = upsert_points(client, collection, points)
                pushed_doc += upserted
                logger.debug("push_batch_done", doc_hash=doc_hash, batch=len(points))
            except Exception as e:
                logger.error("push_upsert_failed", doc_hash=doc_hash, error=str(e))
                per_doc[doc_hash] = {"pushed": pushed_doc, "chunks": len(all_chunks), "status": "upsert_error", "error": str(e)}
                break
        
        pushed_total += pushed_doc
        
        # Determine status
        if pushed_doc >= len(all_chunks) and len(all_chunks) > 0:
            status = "present"
        elif pushed_doc > 0:
            status = "partial"
        else:
            status = "error"
        
        # Update manifest
        if mark_manifest_vector_fn and pushed_doc > 0:
            try:
                mark_manifest_vector_fn(doc_hash, collection, status)
                logger.debug("push_manifest_updated", doc_hash=doc_hash, status=status)
            except Exception as e:
                logger.error("push_manifest_update_failed", doc_hash=doc_hash, error=str(e))
        
        per_doc[doc_hash] = {
            "pushed": pushed_doc,
            "chunks": len(all_chunks),
            "status": status,
        }
    
    skipped = len([h for h in doc_hashes if not chunks_by_hash.get(h)])
    
    logger.info("push_done", pushed=pushed_total, skipped=skipped)
    
    return {
        "pushed": pushed_total,
        "skipped": skipped,
        "per_doc": per_doc,
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Load chunks into Qdrant")
    parser.add_argument("--config", default="vector/settings.yaml", help="Qdrant config path")
    parser.add_argument("--input", required=True, help="JSONL input file")
    
    args = parser.parse_args()
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    
    # Load config
    config = load_yaml_with_env(args.config)
    
    # Load into Qdrant
    loader = QdrantLoader(config)
    loader.load_from_file(Path(args.input))
    
    print(f"Loaded chunks from {args.input} into Qdrant")


if __name__ == "__main__":
    main()

