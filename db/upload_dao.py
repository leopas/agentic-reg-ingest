# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Data Access Objects for vision upload operations."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import VisionUpload


class VisionUploadDAO:
    """DAO for VisionUpload operations."""
    
    @staticmethod
    def create(
        session: Session,
        upload_id: str,
        original_filename: str,
        file_path: str,
        file_hash: str,
        file_size: int,
        mime_type: Optional[str] = None,
    ) -> VisionUpload:
        """Create new vision upload record."""
        upload = VisionUpload(
            upload_id=upload_id,
            original_filename=original_filename,
            file_path=file_path,
            file_hash=file_hash,
            file_size=file_size,
            mime_type=mime_type,
        )
        session.add(upload)
        session.flush()
        return upload
    
    @staticmethod
    def find_by_upload_id(session: Session, upload_id: str) -> Optional[VisionUpload]:
        """Find upload by ID."""
        stmt = select(VisionUpload).where(VisionUpload.upload_id == upload_id)
        return session.scalar(stmt)
    
    @staticmethod
    def find_by_file_hash(session: Session, file_hash: str) -> Optional[VisionUpload]:
        """Find upload by file hash."""
        stmt = select(VisionUpload).where(VisionUpload.file_hash == file_hash)
        return session.scalar(stmt)
    
    @staticmethod
    def update_status(
        session: Session,
        upload_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        """Update upload status."""
        upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
        if upload:
            upload.status = status
            if error_message:
                upload.error_message = error_message
            if status == "completed":
                upload.completed_at = datetime.utcnow()
            session.flush()
    
    @staticmethod
    def update_stage(
        session: Session,
        upload_id: str,
        stage_name: str,
        stage_status: str,
    ) -> None:
        """Update specific pipeline stage."""
        upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
        if upload:
            setattr(upload, f"stage_{stage_name}", stage_status)
            session.flush()
    
    @staticmethod
    def update_artifacts(
        session: Session,
        upload_id: str,
        jsonl_path: Optional[str] = None,
        txt_output_dir: Optional[str] = None,
        plan_id: Optional[str] = None,
    ) -> None:
        """Update output artifact paths."""
        upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
        if upload:
            if jsonl_path is not None:
                upload.jsonl_path = jsonl_path
            if txt_output_dir is not None:
                upload.txt_output_dir = txt_output_dir
            if plan_id is not None:
                upload.plan_id = plan_id
            session.flush()
    
    @staticmethod
    def get_recent(session: Session, limit: int = 50) -> List[VisionUpload]:
        """Get recent uploads."""
        stmt = (
            select(VisionUpload)
            .order_by(VisionUpload.created_at.desc())
            .limit(limit)
        )
        return list(session.scalars(stmt))
    
    @staticmethod
    def get_with_filters(
        session: Session,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> List[VisionUpload]:
        """
        Get uploads with filters.
        
        Args:
            session: DB session
            status: Filter by status (optional)
            search: Search in filename or upload_id (optional)
            limit: Maximum results
            
        Returns:
            Filtered list of uploads
        """
        stmt = select(VisionUpload)
        
        # Apply status filter
        if status:
            stmt = stmt.where(VisionUpload.status == status)
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                (VisionUpload.original_filename.like(search_pattern)) |
                (VisionUpload.upload_id.like(search_pattern))
            )
        
        stmt = stmt.order_by(VisionUpload.created_at.desc()).limit(limit)
        
        return list(session.scalars(stmt))
    
    @staticmethod
    def get_upload_summary(session: Session, upload_id: str) -> Optional[dict]:
        """
        Get complete upload summary with URLs and chunks.
        
        Args:
            session: DB session
            upload_id: Upload ID
            
        Returns:
            Dictionary with upload + URLs + chunks details
        """
        upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
        
        if not upload:
            return None
        
        # Get approved URLs if plan exists
        urls_data = []
        if upload.plan_id:
            from db.dao import AgenticIterDAO
            from db.models import SearchResult, ChunkManifest
            from sqlalchemy import select
            
            # Get approved URLs from iterations
            iters = AgenticIterDAO.get_iters(session, upload.plan_id)
            all_urls = set()
            for it in iters:
                all_urls.update(it.get("approved_urls", []))
            
            # Get details for each URL
            if all_urls:
                stmt = select(SearchResult).where(SearchResult.url.in_(list(all_urls)))
                search_results = list(session.scalars(stmt))
                
                for sr in search_results:
                    # Find corresponding chunk manifest
                    manifest = session.query(ChunkManifest).filter_by(canonical_url=sr.url).first()
                    
                    url_info = {
                        "url": sr.url,
                        "title": sr.title or "Sem título",
                        "snippet": sr.snippet or "",
                        "domain": sr.url.split("/")[2] if "/" in sr.url else "",
                        "final_type": sr.final_type,
                        "score": float(sr.score) if sr.score else 0.0,
                        "scrape_status": "not_started",
                        "doc_hash": None,
                        "chunk_count": 0,
                        "vector_status": "none",
                    }
                    
                    if manifest:
                        url_info.update({
                            "scrape_status": manifest.status,
                            "doc_hash": manifest.doc_hash,
                            "chunk_count": manifest.chunk_count,
                            "vector_status": manifest.vector_status,
                            "source_pipeline": manifest.source_pipeline,
                        })
                    
                    urls_data.append(url_info)
        
        return {
            "upload": {
                "upload_id": upload.upload_id,
                "filename": upload.original_filename,
                "file_size": upload.file_size,
                "status": upload.status,
                "stage_ocr": upload.stage_ocr,
                "stage_multimodal": upload.stage_multimodal,
                "stage_allowlist": upload.stage_allowlist,
                "stage_agentic": upload.stage_agentic,
                "stage_scrape": upload.stage_scrape,
                "stage_vector": upload.stage_vector,
                "jsonl_path": upload.jsonl_path,
                "plan_id": upload.plan_id,
                "error_message": upload.error_message,
                "created_at": upload.created_at.isoformat() if upload.created_at else None,
                "completed_at": upload.completed_at.isoformat() if upload.completed_at else None,
            },
            "urls": urls_data,
            "stats": {
                "total_urls": len(urls_data),
                "scraped": sum(1 for u in urls_data if u["scrape_status"] == "done"),
                "vectorized": sum(1 for u in urls_data if u["vector_status"] == "present"),
                "total_chunks": sum(u["chunk_count"] for u in urls_data),
            }
        }
    
    @staticmethod
    def delete(session: Session, upload_id: str) -> bool:
        """
        Delete upload and all related data.
        
        Args:
            session: Database session
            upload_id: Upload ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
        
        if not upload:
            return False
        
        # Delete the record
        session.delete(upload)
        session.commit()
        
        return True

