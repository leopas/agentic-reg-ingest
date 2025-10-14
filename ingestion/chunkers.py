"""Text chunking utilities with token-aware splitting."""

import structlog
import tiktoken
from typing import Any, Dict, List, Optional

logger = structlog.get_logger()


class TokenAwareChunker:
    """Chunk text based on token counts with overlap."""
    
    def __init__(
        self,
        min_tokens: int = 100,
        max_tokens: int = 512,
        overlap_tokens: int = 50,
        encoding: str = "cl100k_base",
    ):
        """
        Initialize chunker.
        
        Args:
            min_tokens: Minimum chunk size in tokens
            max_tokens: Maximum chunk size in tokens
            overlap_tokens: Overlap between chunks in tokens
            encoding: Tiktoken encoding name
        """
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoder = tiktoken.get_encoding(encoding)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
    
    def chunk(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        anchors: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Chunk text into token-sized pieces with optional anchor-aware splitting.
        
        Args:
            text: Input text
            metadata: Optional metadata to attach to each chunk
            anchors: Optional list of anchor dicts with 'type' and 'value' keys
            
        Returns:
            List of chunks with text and metadata
        """
        # Validate input
        if not text or not text.strip():
            logger.warning("chunker_empty_text")
            raise ValueError("Cannot chunk empty text")
        
        try:
            # Encode to tokens
            tokens = self.encoder.encode(text)
        except Exception as e:
            logger.error(
                "chunker_encode_failed",
                error_type=type(e).__name__,
                error_message=str(e),
                text_preview=text[:200] if text else "",
            )
            raise ValueError(f"Failed to encode text: {e}")
        
        if len(tokens) == 0:
            logger.warning("chunker_no_tokens")
            raise ValueError("Text encoded to zero tokens")
        
        if len(tokens) <= self.max_tokens:
            # Text fits in one chunk
            return [{
                "text": text,
                "tokens": len(tokens),
                "chunk_index": 0,
                "total_chunks": 1,
                **(metadata or {}),
            }]
        
        # If anchors provided, try anchor-aware splitting
        if anchors:
            return self._chunk_with_anchors_aware(text, tokens, anchors, metadata)
        
        # Otherwise, standard token window chunking
        return self._chunk_standard(text, tokens, metadata)
    
    def _chunk_standard(
        self,
        text: str,
        tokens: List[int],
        metadata: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Standard token window chunking without anchors."""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(tokens):
            # Get chunk tokens
            end = min(start + self.max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            try:
                chunk_text = self.encoder.decode(chunk_tokens)
            except Exception as e:
                logger.error(
                    "chunker_decode_failed",
                    chunk_index=chunk_index,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise ValueError(f"Failed to decode chunk {chunk_index}: {e}")
            
            chunks.append({
                "text": chunk_text,
                "tokens": len(chunk_tokens),
                "chunk_index": chunk_index,
                "start_token": start,
                "end_token": end,
                **(metadata or {}),
            })
            
            # Move to next chunk with overlap
            start += self.max_tokens - self.overlap_tokens
            chunk_index += 1
        
        # Update total_chunks
        for chunk in chunks:
            chunk["total_chunks"] = len(chunks)
        
        return chunks
    
    def _chunk_with_anchors_aware(
        self,
        text: str,
        tokens: List[int],
        anchors: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Anchor-aware chunking: try to start new chunks near headings/tables.
        
        Strategy:
        1. Find approximate character positions of anchor texts in document
        2. Convert char positions to token positions
        3. Try to start chunks near anchor boundaries
        4. Still respect min/max token limits
        """
        # Find anchor positions in text
        anchor_positions = []
        for anchor in anchors:
            anchor_text = anchor.get("value", "")
            if not anchor_text:
                continue
            
            # Find this anchor in the text
            pos = text.find(anchor_text)
            if pos >= 0:
                anchor_positions.append({
                    "char_pos": pos,
                    "anchor": anchor,
                })
        
        # Sort by position
        anchor_positions.sort(key=lambda x: x["char_pos"])
        
        if not anchor_positions:
            # No anchors found in text, fallback to standard
            logger.debug("no_anchors_found_in_text", anchors_count=len(anchors))
            return self._chunk_standard(text, tokens, metadata)
        
        # Convert character positions to approximate token positions
        # This is approximate since tokenization doesn't map 1:1 to characters
        text_len = len(text)
        token_positions = []
        for ap in anchor_positions:
            # Approximate token position based on character ratio
            approx_token_pos = int((ap["char_pos"] / text_len) * len(tokens))
            token_positions.append({
                "token_pos": approx_token_pos,
                "anchor": ap["anchor"],
            })
        
        # Create chunks respecting anchor boundaries
        chunks = []
        start = 0
        chunk_index = 0
        next_anchor_idx = 0
        
        while start < len(tokens):
            # Look for next anchor within reasonable range
            preferred_end = start + self.max_tokens
            
            # Check if there's an anchor between start and preferred_end
            split_at = None
            while next_anchor_idx < len(token_positions):
                anchor_pos = token_positions[next_anchor_idx]["token_pos"]
                
                if anchor_pos <= start:
                    # Already passed this anchor
                    next_anchor_idx += 1
                    continue
                
                if start + self.min_tokens <= anchor_pos <= preferred_end:
                    # Good split point: anchor within valid range
                    split_at = anchor_pos
                    next_anchor_idx += 1
                    break
                
                if anchor_pos > preferred_end:
                    # Anchor too far, use max_tokens
                    break
                
                next_anchor_idx += 1
            
            if split_at:
                end = split_at
            else:
                end = min(preferred_end, len(tokens))
            
            chunk_tokens = tokens[start:end]
            
            try:
                chunk_text = self.encoder.decode(chunk_tokens)
            except Exception as e:
                logger.error(
                    "chunker_decode_failed",
                    chunk_index=chunk_index,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise ValueError(f"Failed to decode chunk {chunk_index}: {e}")
            
            chunks.append({
                "text": chunk_text,
                "tokens": len(chunk_tokens),
                "chunk_index": chunk_index,
                "start_token": start,
                "end_token": end,
                **(metadata or {}),
            })
            
            # Move to next chunk with overlap
            start += len(chunk_tokens) - self.overlap_tokens
            chunk_index += 1
        
        # Update total_chunks
        for chunk in chunks:
            chunk["total_chunks"] = len(chunks)
        
        logger.debug(
            "anchor_aware_chunking_done",
            chunks_count=len(chunks),
            anchors_used=len(anchor_positions),
        )
        
        return chunks
    
    def chunk_with_anchors(
        self,
        segments: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Chunk text segments that were split by anchors.
        
        Args:
            segments: List of segments from AnchorDetector
            
        Returns:
            List of chunks with anchor metadata
        """
        all_chunks = []
        
        for seg_idx, segment in enumerate(segments):
            text = segment["text"]
            anchor = segment.get("anchor")
            
            # Create metadata
            metadata = {
                "segment_index": seg_idx,
                "anchor_type": anchor["type"] if anchor else None,
                "anchor_text": anchor["matched_text"] if anchor else None,
            }
            
            # Chunk this segment
            chunks = self.chunk(text, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks

