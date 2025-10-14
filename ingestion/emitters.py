"""Output emitters for knowledge base data."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class JSONLEmitter:
    """Emit chunks as JSONL (one JSON object per line)."""
    
    def __init__(self, output_path: str | Path):
        """
        Initialize emitter.
        
        Args:
            output_path: Path to output JSONL file
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def emit_chunk(
        self,
        chunk: Dict[str, Any],
        source_url: str,
        source_file: str,
        append: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit a single chunk to JSONL.
        
        Args:
            chunk: Chunk dictionary
            source_url: Source document URL
            source_file: Local file path (if downloaded)
            append: Append to file (True) or overwrite (False)
            metadata: Additional metadata (content_type, extracted_by, etc.)
        """
        record = {
            "text": chunk["text"],
            "tokens": chunk["tokens"],
            "chunk_index": chunk["chunk_index"],
            "total_chunks": chunk.get("total_chunks", 1),
            "source_url": source_url,
            "source_file": source_file,
            "segment_index": chunk.get("segment_index"),
            "anchor_type": chunk.get("anchor_type"),
            "anchor_text": chunk.get("anchor_text"),
        }
        
        # Add metadata if provided
        if metadata:
            record["metadata"] = metadata
        
        mode = 'a' if append else 'w'
        
        with open(self.output_path, mode, encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def emit_chunks(
        self,
        chunks: List[Dict[str, Any]],
        source_url: str,
        source_file: str,
        append: bool = True,
        anchors: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit multiple chunks to JSONL.
        
        Args:
            chunks: List of chunk dictionaries
            source_url: Source document URL
            source_file: Local file path
            append: Append to file
            anchors: Optional list of anchors detected in document
            metadata: Optional metadata (content_type, extracted_by, etc.)
        """
        # Add anchors info to metadata if provided
        if metadata is None:
            metadata = {}
        
        if anchors:
            metadata["anchors_count"] = len(anchors)
            metadata["anchors"] = anchors
        
        for chunk in chunks:
            self.emit_chunk(chunk, source_url, source_file, append=append, metadata=metadata)
            # After first chunk, always append
            append = True
    
    def clear(self) -> None:
        """Clear output file."""
        if self.output_path.exists():
            self.output_path.unlink()

