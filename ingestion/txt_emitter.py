# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Text emitter for enrichment pipeline."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()


class TXTEmitter:
    """Emitter for normalized text files with metadata header."""
    
    def __init__(self, output_base_dir: str):
        """
        Initialize TXT emitter.
        
        Args:
            output_base_dir: Base directory for output (e.g., data/output/enrichment_txt)
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
    
    def emit(
        self,
        upload_id: str,
        doc_num: int,
        url: str,
        domain: str,
        fetched_at: str,
        doc_hash: str,
        text: str,
    ) -> str:
        """
        Emit normalized text file with metadata header.
        
        Args:
            upload_id: Upload session ID
            doc_num: Document number
            url: Source URL
            domain: Domain name
            fetched_at: ISO8601 timestamp
            doc_hash: SHA256 hash of content
            text: Normalized text content
            
        Returns:
            Path to emitted file
        """
        # Create upload-specific directory
        upload_dir = self.output_base_dir / upload_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"doc_{doc_num:04d}.txt"
        output_path = upload_dir / filename
        
        logger.info("txt_emit_start", upload_id=upload_id, doc_num=doc_num, path=str(output_path))
        
        try:
            # Build content with metadata header
            content = self._build_content_with_header(
                url=url,
                domain=domain,
                fetched_at=fetched_at,
                doc_hash=doc_hash,
                text=text,
            )
            
            # Write file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info("txt_emit_done", path=str(output_path), size=len(content))
            
            return str(output_path)
        
        except Exception as e:
            logger.error("txt_emit_failed", upload_id=upload_id, doc_num=doc_num, error=str(e))
            raise
    
    def _build_content_with_header(
        self,
        url: str,
        domain: str,
        fetched_at: str,
        doc_hash: str,
        text: str,
    ) -> str:
        """
        Build file content with metadata header.
        
        Args:
            url: Source URL
            domain: Domain name
            fetched_at: ISO8601 timestamp
            doc_hash: Content hash
            text: Normalized text
            
        Returns:
            Full file content with header
        """
        header = f"""===META===
url: {url}
fetched_at: {fetched_at}
domain: {domain}
doc_hash: {doc_hash}
===CONTENT===
"""
        
        return header + text
    
    def check_exists(self, upload_id: str, doc_hash: str) -> bool:
        """
        Check if document with hash already exists in upload directory.
        
        Args:
            upload_id: Upload session ID
            doc_hash: Document hash to check
            
        Returns:
            True if exists, False otherwise
        """
        upload_dir = self.output_base_dir / upload_id
        
        if not upload_dir.exists():
            return False
        
        # Scan all .txt files in directory
        for txt_file in upload_dir.glob("*.txt"):
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    content = f.read(500)  # Read header only
                    
                    if f"doc_hash: {doc_hash}" in content:
                        logger.info("txt_exists_skip", doc_hash=doc_hash[:16], file=txt_file.name)
                        return True
            except Exception:
                continue
        
        return False

