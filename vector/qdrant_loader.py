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

