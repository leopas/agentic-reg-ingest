# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Vision enrichment API routes."""

import hashlib
import os
import uuid
from pathlib import Path
from typing import Any, List, Optional

import structlog
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from apps.api.schemas.vision_enrichment import (
    PipelineStatusResponse,
    UploadJobResponse,
    VectorPushRequest,
)
from common.env_readers import load_yaml_with_env
from db.upload_dao import VisionUploadDAO
from db.session import DatabaseSession
from pipelines.enrichment_pipeline import EnrichmentPipeline

logger = structlog.get_logger()

router = APIRouter()


@router.get("/ui/vision-enrichment", include_in_schema=False)
async def vision_enrichment_ui():
    """Render Vision Enrichment UI page."""
    ui_file = Path(__file__).parent / "templates" / "vision_enrichment.html"
    
    if not ui_file.exists():
        raise HTTPException(status_code=404, detail="Vision Enrichment UI not found")
    
    return FileResponse(ui_file)


@router.get("/ui/vision-admin", include_in_schema=False)
async def vision_admin_ui():
    """Render Vision Administration UI page."""
    ui_file = Path(__file__).parent / "templates" / "vision_admin.html"
    
    if not ui_file.exists():
        raise HTTPException(status_code=404, detail="Vision Admin UI not found")
    
    return FileResponse(ui_file)


@router.post("/vision/upload", response_model=UploadJobResponse)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    """
    Upload files for vision enrichment.
    
    Args:
        files: List of uploaded files (.pdf, .pptx, .zip)
        
    Returns:
        Upload job ID and status
    """
    try:
        logger.info("vision_upload_start", files_count=len(files))
        
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        # Load config
        config = load_yaml_with_env("configs/vision_enrichment.yaml")
        
        upload_dir = Path(config.get("upload", {}).get("upload_dir", "data/uploads"))
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        max_size_mb = config.get("upload", {}).get("max_file_size_mb", 50)
        allowed_exts = config.get("upload", {}).get("allowed_extensions", [".pdf", ".pptx", ".ppt", ".zip"])
        
        # Process first file (for simplicity, process one at a time)
        file = files[0]
        
        # Validate extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_exts)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        if file_size > max_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {max_size_mb}MB"
            )
        
        # Compute hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Check if already uploaded
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            existing = VisionUploadDAO.find_by_file_hash(session, file_hash)
            
            if existing:
                logger.info("vision_upload_duplicate", upload_id=existing.upload_id, file_hash=file_hash[:16])
                return UploadJobResponse(
                    upload_id=existing.upload_id,
                    status=existing.status,
                    message="File already uploaded (duplicate detected)",
                )
            
            # Generate upload ID
            upload_id = str(uuid.uuid4())
            
            # Sanitize filename
            safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ")
            safe_filename = safe_filename[:100]  # Limit length
            
            # Save file
            file_path = upload_dir / f"{upload_id}_{safe_filename}"
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info("vision_upload_saved", upload_id=upload_id, path=str(file_path))
            
            # Create database record
            VisionUploadDAO.create(
                session,
                upload_id=upload_id,
                original_filename=file.filename,
                file_path=str(file_path),
                file_hash=file_hash,
                file_size=file_size,
                mime_type=file.content_type,
            )
            
            session.commit()
        
        logger.info("vision_upload_done", upload_id=upload_id)
        
        return UploadJobResponse(
            upload_id=upload_id,
            status="uploaded",
            message=f"File uploaded successfully. Upload ID: {upload_id}",
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/run/{upload_id}")
async def run_enrichment_pipeline(
    upload_id: str,
    background_tasks: BackgroundTasks,
):
    """
    Run enrichment pipeline for uploaded file.
    
    Args:
        upload_id: Upload ID
        
    Returns:
        Confirmation message
    """
    try:
        logger.info("vision_run_start", upload_id=upload_id)
        
        # Verify upload exists
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            if upload.status == "processing":
                raise HTTPException(status_code=409, detail="Pipeline already running")
        
        # Load config and run pipeline in background
        config = load_yaml_with_env("configs/vision_enrichment.yaml")
        
        pipeline = EnrichmentPipeline(config)
        background_tasks.add_task(pipeline.run, upload_id)
        
        logger.info("vision_run_scheduled", upload_id=upload_id)
        
        return {
            "upload_id": upload_id,
            "status": "scheduled",
            "message": "Pipeline scheduled for execution",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_run_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/status/{upload_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(upload_id: str):
    """
    Get pipeline status for upload.
    
    Args:
        upload_id: Upload ID
        
    Returns:
        Pipeline status with stage progress
    """
    try:
        logger.info("vision_status_check", upload_id=upload_id)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            return PipelineStatusResponse(
                upload_id=upload.upload_id,
                status=upload.status,
                stage_ocr=upload.stage_ocr,
                stage_multimodal=upload.stage_multimodal,
                stage_allowlist=upload.stage_allowlist,
                stage_agentic=upload.stage_agentic,
                stage_scrape=upload.stage_scrape,
                stage_vector=upload.stage_vector,
                jsonl_path=upload.jsonl_path,
                txt_output_dir=upload.txt_output_dir,
                plan_id=upload.plan_id,
                error_message=upload.error_message,
                created_at=upload.created_at,
                updated_at=upload.updated_at,
                completed_at=upload.completed_at,
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_status_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/vector/push/{upload_id}")
async def push_to_vector(
    upload_id: str,
    background_tasks: BackgroundTasks,
    collection: str = "kb_regulatory",
    overwrite: bool = False,
):
    """
    Push enriched documents to vector database.
    
    Args:
        upload_id: Upload ID
        collection: Qdrant collection name
        overwrite: Overwrite existing vectors
        
    Returns:
        Push result
    """
    try:
        logger.info("vision_vector_push_start", upload_id=upload_id, collection=collection)
        
        # Verify upload exists and is completed
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            if upload.status != "completed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Pipeline not completed. Current status: {upload.status}"
                )
        
        # Load config and push in background
        config = load_yaml_with_env("configs/vision_enrichment.yaml")
        
        pipeline = EnrichmentPipeline(config)
        background_tasks.add_task(
            pipeline.push_to_vector,
            upload_id,
            collection,
            overwrite,
        )
        
        logger.info("vision_vector_push_scheduled", upload_id=upload_id)
        
        return {
            "upload_id": upload_id,
            "status": "scheduled",
            "message": "Vector push scheduled",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_vector_push_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/download/jsonl/{upload_id}")
async def download_jsonl(upload_id: str):
    """
    Download JSONL output for upload.
    
    Args:
        upload_id: Upload ID
        
    Returns:
        JSONL file
    """
    try:
        logger.info("vision_download_jsonl", upload_id=upload_id)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            if not upload.jsonl_path:
                raise HTTPException(status_code=404, detail="JSONL not yet generated")
            
            jsonl_path = Path(upload.jsonl_path)
            
            if not jsonl_path.exists():
                raise HTTPException(status_code=404, detail="JSONL file not found")
            
            return FileResponse(
                path=str(jsonl_path),
                filename=f"{upload_id}.jsonl",
                media_type="application/x-ndjson",
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_download_jsonl_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/reset/{upload_id}")
async def reset_upload_status(upload_id: str):
    """
    Reset upload status to allow reprocessing.
    
    Args:
        upload_id: Upload ID to reset
        
    Returns:
        Confirmation message
    """
    try:
        logger.info("vision_reset_start", upload_id=upload_id)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            # Reset to uploaded status and clear all stages
            VisionUploadDAO.update_status(session, upload_id, "uploaded", error_message=None)
            
            # Reset all stages to pending
            for stage in ["ocr", "multimodal", "allowlist", "agentic", "scrape", "vector"]:
                VisionUploadDAO.update_stage(session, upload_id, stage, "pending")
            
            session.commit()
            
            logger.info("vision_reset_done", upload_id=upload_id)
            
            return {
                "upload_id": upload_id,
                "status": "reset",
                "message": "Upload status reset. You can now run the pipeline again.",
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_reset_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/approved-urls/{upload_id}")
async def get_approved_urls(upload_id: str):
    """
    Get approved URLs from agentic search with context.
    
    Args:
        upload_id: Upload ID
        
    Returns:
        List of approved URLs with metadata for review
    """
    try:
        logger.info("vision_approved_urls", upload_id=upload_id)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            if not upload.plan_id:
                raise HTTPException(status_code=404, detail="Agentic search not yet completed")
            
            # Get approved URLs from agentic iterations
            from db.dao import AgenticIterDAO
            from sqlalchemy import select
            from db.models import SearchResult
            
            iters = AgenticIterDAO.get_iters(session, upload.plan_id)
            
            # Collect all approved URLs
            all_approved_urls = set()
            for iteration in iters:
                all_approved_urls.update(iteration.get("approved_urls", []))
            
            # Get details from search_result table
            if all_approved_urls:
                stmt = select(SearchResult).where(
                    SearchResult.url.in_(list(all_approved_urls))
                )
                results = list(session.scalars(stmt))
                
                urls_with_context = []
                for r in results:
                    urls_with_context.append({
                        "url": r.url,
                        "title": r.title or "Sem título",
                        "snippet": r.snippet or "",
                        "domain": r.url.split("/")[2] if "/" in r.url else "",
                        "final_type": r.final_type,
                        "score": float(r.score) if r.score else 0.0,
                        "selected": True,  # Default: todas selecionadas
                    })
                
                return {
                    "upload_id": upload_id,
                    "plan_id": upload.plan_id,
                    "urls": urls_with_context,
                    "total": len(urls_with_context),
                }
            else:
                return {
                    "upload_id": upload_id,
                    "plan_id": upload.plan_id,
                    "urls": [],
                    "total": 0,
                }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_approved_urls_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/scrape/{upload_id}")
async def start_scraping(
    upload_id: str,
    background_tasks: BackgroundTasks,
    selected_urls: List[str] = [],
):
    """
    Start scraping phase with selected URLs.
    
    Args:
        upload_id: Upload ID
        selected_urls: List of URLs to scrape (if empty, scrape all)
        
    Returns:
        Confirmation message
    """
    try:
        logger.info("vision_scrape_start", upload_id=upload_id, selected_count=len(selected_urls))
        
        # Verify upload and stage
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            if upload.stage_agentic != "completed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Agentic search not completed. Stage: {upload.stage_agentic}"
                )
        
        # Load config and run scraping in background
        config = load_yaml_with_env("configs/vision_enrichment.yaml")
        
        from pipelines.enrichment_pipeline import EnrichmentPipeline
        pipeline = EnrichmentPipeline(config)
        
        # Schedule scraping phase
        background_tasks.add_task(
            pipeline._run_scraping_and_vector_phase,
            upload_id,
            selected_urls or None,
        )
        
        logger.info("vision_scrape_scheduled", upload_id=upload_id)
        
        return {
            "upload_id": upload_id,
            "status": "scheduled",
            "message": f"Scraping scheduled for {len(selected_urls) if selected_urls else 'all'} URLs",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_scrape_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/admin/uploads")
async def admin_list_uploads(
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
):
    """
    List uploads with filters for admin panel.
    
    Args:
        status: Filter by status (uploaded, processing, awaiting_review, completed, failed)
        search: Search in filename or upload_id
        limit: Maximum results
        
    Returns:
        Filtered list of uploads
    """
    try:
        logger.info("vision_admin_uploads", status=status, search=search, limit=limit)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            uploads = VisionUploadDAO.get_with_filters(session, status, search, limit)
            
            result = []
            for upload in uploads:
                # Count URLs if plan exists
                url_count = 0
                if upload.plan_id:
                    from db.dao import AgenticIterDAO
                    iters = AgenticIterDAO.get_iters(session, upload.plan_id)
                    all_urls = set()
                    for it in iters:
                        all_urls.update(it.get("approved_urls", []))
                    url_count = len(all_urls)
                
                result.append({
                    "upload_id": upload.upload_id,
                    "filename": upload.original_filename,
                    "status": upload.status,
                    "created_at": upload.created_at.isoformat(),
                    "completed_at": upload.completed_at.isoformat() if upload.completed_at else None,
                    "url_count": url_count,
                    "has_error": bool(upload.error_message),
                })
            
            return {
                "count": len(result),
                "uploads": result,
            }
    
    except Exception as e:
        logger.error("vision_admin_uploads_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/admin/upload-details/{upload_id}")
async def admin_upload_details(upload_id: str):
    """
    Get complete upload details for admin panel.
    
    Args:
        upload_id: Upload ID
        
    Returns:
        Complete upload summary with URLs and chunks
    """
    try:
        logger.info("vision_admin_details", upload_id=upload_id)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            summary = VisionUploadDAO.get_upload_summary(session, upload_id)
            
            if not summary:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_admin_details_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/admin/chunk-preview/{doc_hash}")
async def admin_chunk_preview(doc_hash: str, max_chars: int = 500):
    """
    Get preview of chunk content.
    
    Args:
        doc_hash: Document hash
        max_chars: Maximum characters to return
        
    Returns:
        Preview text
    """
    try:
        logger.info("vision_admin_preview", doc_hash=doc_hash[:16])
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            from db.dao import ChunkManifestDAO
            
            preview = ChunkManifestDAO.get_chunk_preview(session, doc_hash, max_chars)
            
            if preview is None:
                raise HTTPException(status_code=404, detail="Chunks not found")
            
            return {
                "doc_hash": doc_hash,
                "preview": preview,
                "truncated": len(preview) >= max_chars,
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("vision_admin_preview_failed", doc_hash=doc_hash[:16], error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/admin/re-scrape")
async def admin_re_scrape(
    background_tasks: BackgroundTasks,
    upload_id: str,
    urls: List[str],
):
    """
    Re-scrape specific URLs from an upload.
    
    Args:
        upload_id: Upload ID
        urls: List of URLs to re-scrape
        
    Returns:
        Confirmation
    """
    try:
        logger.info("vision_admin_rescrape", upload_id=upload_id, urls_count=len(urls))
        
        # Load config and schedule
        config = load_yaml_with_env("configs/vision_enrichment.yaml")
        
        from pipelines.enrichment_pipeline import EnrichmentPipeline
        pipeline = EnrichmentPipeline(config)
        
        background_tasks.add_task(
            pipeline._run_scraping_and_vector_phase,
            upload_id,
            urls,
        )
        
        return {
            "upload_id": upload_id,
            "status": "scheduled",
            "message": f"Re-scraping scheduled for {len(urls)} URLs",
        }
    
    except Exception as e:
        logger.error("vision_admin_rescrape_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/list")
async def list_uploads(limit: int = 50):
    """
    List recent uploads.
    
    Args:
        limit: Maximum number of uploads to return
        
    Returns:
        List of uploads
    """
    try:
        logger.info("vision_list_uploads", limit=limit)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            uploads = VisionUploadDAO.get_recent(session, limit=limit)
            
            result = []
            for upload in uploads:
                result.append({
                    "upload_id": upload.upload_id,
                    "filename": upload.original_filename,
                    "status": upload.status,
                    "created_at": upload.created_at.isoformat(),
                    "stage_ocr": upload.stage_ocr,
                    "stage_multimodal": upload.stage_multimodal,
                    "stage_allowlist": upload.stage_allowlist,
                    "stage_agentic": upload.stage_agentic,
                    "stage_scrape": upload.stage_scrape,
                    "stage_vector": upload.stage_vector,
                })
            
            return {
                "count": len(result),
                "uploads": result,
            }
    
    except Exception as e:
        logger.error("vision_list_uploads_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vision/admin/delete/{upload_id}")
async def admin_delete_upload(upload_id: str):
    """
    Delete upload and all related artifacts.
    
    DELETE /vision/admin/delete/{upload_id}
    """
    import shutil
    from pathlib import Path
    
    try:
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            # Get upload details
            upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
            
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")
            
            deleted_items = []
            
            # 1. Delete physical files
            try:
                # Delete original upload file
                if upload.file_path and Path(upload.file_path).exists():
                    Path(upload.file_path).unlink()
                    deleted_items.append(f"Arquivo original: {upload.original_filename}")
                
                # Delete JSONL
                if upload.jsonl_path and Path(upload.jsonl_path).exists():
                    Path(upload.jsonl_path).unlink()
                    deleted_items.append("JSONL de análise")
                
                # Delete TXT output directory
                if upload.txt_output_dir and Path(upload.txt_output_dir).exists():
                    shutil.rmtree(upload.txt_output_dir)
                    deleted_items.append(f"Diretório de TXTs: {Path(upload.txt_output_dir).name}")
                    
            except Exception as e:
                logger.warning("admin_delete_files_partial", error=str(e))
                deleted_items.append(f"⚠️ Alguns arquivos não puderam ser removidos: {str(e)}")
            
            # 2. Delete from database (cascade will handle related records)
            VisionUploadDAO.delete(session, upload_id)
            deleted_items.append("Registro no banco de dados")
            
            # 3. TODO: Delete chunks from Qdrant (if implemented)
            # This would require tracking which chunks belong to this upload
            
            logger.info("admin_delete_success", upload_id=upload_id, filename=upload.original_filename)
            
            return {
                "ok": True,
                "upload_id": upload_id,
                "filename": upload.original_filename,
                "deleted_items": deleted_items,
                "message": f"Upload excluído com sucesso! {len(deleted_items)} itens removidos."
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("admin_delete_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

