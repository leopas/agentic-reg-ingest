# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Anchor detection and extraction from documents."""

import re
from typing import Any, Dict, List, Optional


class AnchorDetector:
    """Detect structural anchors in document text."""
    
    def __init__(self, markers: List[Dict[str, Any]]):
        """
        Initialize anchor detector with markers.
        
        Args:
            markers: List of marker dicts with 'type', 'pattern', 'confidence'
        """
        self.markers = markers
        self.compiled_patterns = [
            {
                "type": m["type"],
                "pattern": re.compile(m["pattern"], re.IGNORECASE | re.MULTILINE),
                "confidence": m.get("confidence", 0.5),
            }
            for m in markers
        ]
    
    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect anchors in text.
        
        Args:
            text: Document text
            
        Returns:
            List of detected anchors with position, type, and matched text
        """
        anchors = []
        
        for marker in self.compiled_patterns:
            for match in marker["pattern"].finditer(text):
                anchors.append({
                    "type": marker["type"],
                    "matched_text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": marker["confidence"],
                })
        
        # Sort by position
        anchors.sort(key=lambda a: a["start"])
        
        return anchors
    
    def segment_by_anchors(
        self,
        text: str,
        min_segment_length: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Segment text by detected anchors.
        
        Args:
            text: Document text
            min_segment_length: Minimum segment length in characters
            
        Returns:
            List of segments with anchor metadata
        """
        anchors = self.detect(text)
        
        if not anchors:
            # No anchors, return whole text as one segment
            return [{
                "text": text,
                "anchor": None,
                "start": 0,
                "end": len(text),
            }]
        
        segments = []
        
        for i, anchor in enumerate(anchors):
            # Segment starts at current anchor
            start = anchor["start"]
            
            # Segment ends at next anchor or end of text
            if i + 1 < len(anchors):
                end = anchors[i + 1]["start"]
            else:
                end = len(text)
            
            segment_text = text[start:end]
            
            # Skip very short segments
            if len(segment_text.strip()) < min_segment_length:
                continue
            
            segments.append({
                "text": segment_text,
                "anchor": anchor,
                "start": start,
                "end": end,
            })
        
        return segments

