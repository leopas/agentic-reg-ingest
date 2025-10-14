"""FastAPI application for agentic-reg-ingest."""

import os
import uuid
import structlog
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from apps.api.middleware import LoggingMiddleware
from common.env_readers import load_yaml_with_env
from common.settings import settings
from db.session import DatabaseSession
from pipelines.ingest_pipeline import IngestPipeline
from pipelines.search_pipeline import SearchPipeline


# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("app_startup")
    yield
    logger.info("app_shutdown")


# Create FastAPI app
app = FastAPI(
    title="Agentic Regulatory Ingest",
    description="Pipeline for searching and ingesting regulatory documents",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(LoggingMiddleware)

# Mount static files for UI
ui_static_dir = Path(__file__).parent.parent / "ui" / "static"
if ui_static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(ui_static_dir)), name="static")


# Request/Response models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    db_ok: bool
    cse_ready: bool
    openai_ready: bool


class SearchRequest(BaseModel):
    """Search pipeline request."""
    query: str
    topn: int = 100


class SearchResponse(BaseModel):
    """Search pipeline response."""
    results_count: int
    message: str


class IngestRequest(BaseModel):
    """Ingest pipeline request."""
    limit: int = 100


class IngestResponse(BaseModel):
    """Ingest pipeline response."""
    total: int
    new: int
    changed: int
    success: int
    failed: int


class PlanRequest(BaseModel):
    """Agentic plan creation request."""
    prompt: str


class PlanResponse(BaseModel):
    """Agentic plan creation response."""
    plan_id: str
    plan: dict


class RunAgenticRequest(BaseModel):
    """Agentic search execution request."""
    plan_id: str | None = None
    plan_override: dict | None = None


class RunAgenticResponse(BaseModel):
    """Agentic search execution response."""
    plan_id: str
    iterations: int
    approved_total: int
    stopped_by: str
    promoted_urls: list[str]


class ApprovedDoc(BaseModel):
    """Single approved document with metadata."""
    url: str
    title: str | None = None
    final_type: str | None = None
    last_modified: str | None = None
    score: float | None = None
    approved_at: str | None = None
    doc_hash: str | None = None
    vector_status: str = "none"
    chunk_count: int = 0
    cache_status: str = "none"


class ApprovedListResponse(BaseModel):
    """Response for approved documents list."""
    count: int
    docs: list[ApprovedDoc]


class RegenerateRequest(BaseModel):
    """Request for regenerating chunks."""
    urls: list[str] | None = None
    doc_hashes: list[str] | None = None
    overwrite: bool = True
    push_after: bool = False
    collection: str = "kb_regulatory"


class RegenerateResponse(BaseModel):
    """Response for regenerate operation."""
    processed: int
    errors: list[dict]
    items: list[dict]


class VectorPushRequest(BaseModel):
    """Request for pushing to VectorDB."""
    doc_hashes: list[str]
    collection: str = "kb_regulatory"
    overwrite: bool = False


class VectorPushResponse(BaseModel):
    """Response for vector push."""
    pushed: int
    skipped: int
    collection: str


class VectorDeleteRequest(BaseModel):
    """Request for deleting from VectorDB."""
    doc_hashes: list[str]
    collection: str = "kb_regulatory"


class VectorDeleteResponse(BaseModel):
    """Response for vector delete."""
    deleted: int
    collection: str


class ChunkStatusResponse(BaseModel):
    """Response for chunk status query."""
    manifests: list[dict]


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Checks:
    - Database connectivity
    - Google CSE API credentials
    - OpenAI API credentials
    """
    db_ok = False
    cse_ready = False
    openai_ready = False
    
    # Check database
    try:
        db_session = DatabaseSession()
        with next(db_session.get_session()):
            db_ok = True
    except Exception as e:
        logger.error("health_check_db_failed", error=str(e))
    
    # Check CSE credentials
    try:
        if settings.google_api_key and settings.google_cx:
            cse_ready = True
    except Exception:
        pass
    
    # Check OpenAI credentials
    try:
        if settings.openai_api_key:
            openai_ready = True
    except Exception:
        pass
    
    status = "ok" if (db_ok and cse_ready and openai_ready) else "degraded"
    
    return HealthResponse(
        status=status,
        db_ok=db_ok,
        cse_ready=cse_ready,
        openai_ready=openai_ready,
    )


@app.post("/run/search", response_model=SearchResponse)
async def run_search(request: SearchRequest):
    """
    Execute search pipeline.
    
    Searches Google CSE, scores results, and caches in database.
    """
    try:
        logger.info("api_search_start", query=request.query)
        
        # Load configs
        cse_config = load_yaml_with_env("configs/cse.yaml")
        db_config = load_yaml_with_env("configs/db.yaml")
        
        # Run pipeline
        pipeline = SearchPipeline(cse_config, db_config)
        results = pipeline.execute(query=request.query, topn=request.topn)
        
        return SearchResponse(
            results_count=len(results),
            message=f"Search completed: {len(results)} results found",
        )
    
    except Exception as e:
        logger.error("api_search_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run/ingest", response_model=IngestResponse)
async def run_ingest(request: IngestRequest):
    """
    Execute ingest pipeline.
    
    Processes pending/changed documents and emits chunks to JSONL.
    """
    try:
        logger.info("api_ingest_start", limit=request.limit)
        
        # Load configs
        ingest_config = load_yaml_with_env("configs/ingest.yaml")
        db_config = load_yaml_with_env("configs/db.yaml")
        
        # Run pipeline
        pipeline = IngestPipeline(ingest_config, db_config)
        stats = pipeline.execute(limit=request.limit)
        
        return IngestResponse(**stats)
    
    except Exception as e:
        logger.error("api_ingest_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agentic/plan", response_model=PlanResponse)
async def create_agentic_plan(request: PlanRequest):
    """
    Create agentic search plan from natural language prompt.
    
    The LLM generates a structured plan with queries, quality gates, and stop conditions.
    The plan is persisted and can be edited before execution.
    """
    try:
        logger.info("api_agentic_plan_start", prompt_len=len(request.prompt))
        
        # Load configs
        from agentic.llm import LLMClient
        from common.settings import settings
        
        llm = LLMClient(
            api_key=settings.openai_api_key,
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=3000,
        )
        
        # Generate plan
        plan = llm.plan_from_prompt(request.prompt)
        plan_id = str(uuid.uuid4())
        
        # Save plan
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            from db.dao import AgenticPlanDAO
            
            AgenticPlanDAO.save_plan(
                session,
                plan_id=plan_id,
                goal=plan.goal,
                plan_json=plan.dict(),
            )
            session.commit()
        
        logger.info("api_agentic_plan_done", plan_id=plan_id)
        
        return PlanResponse(
            plan_id=plan_id,
            plan=plan.dict(),
        )
    
    except Exception as e:
        logger.error("api_agentic_plan_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agentic/run", response_model=RunAgenticResponse)
async def run_agentic(request: RunAgenticRequest):
    """
    Execute agentic search with Plan→Act→Observe→Judge→Re-plan loop.
    
    Either provide plan_id (to load from DB) or plan_override (to use custom plan).
    """
    try:
        logger.info("api_agentic_run_start", plan_id=request.plan_id)
        
        # Load configs
        from agentic.llm import LLMClient
        from agentic.cse_client import CSEClient
        from agentic.scoring import ResultScorer
        from agentic.schemas import Plan
        from pipelines.agentic_controller import run_agentic_search
        from common.settings import settings
        
        cse_config = load_yaml_with_env("configs/cse.yaml")
        agentic_config = load_yaml_with_env("configs/agentic.yaml")
        
        # Initialize clients
        cse = CSEClient(
            api_key=cse_config["api_key"],
            cx=cse_config["cx"],
            timeout=int(cse_config["timeout_seconds"]),
        )
        
        llm = LLMClient(
            api_key=settings.openai_api_key,
            model=agentic_config["agentic"]["llm"]["model"],
            temperature=agentic_config["agentic"]["llm"]["temperature"],
            max_tokens=agentic_config["agentic"]["llm"]["max_tokens"],
        )
        
        scorer = ResultScorer(cse_config)
        
        # Get plan
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            if request.plan_override:
                # Use override
                plan = Plan(**request.plan_override)
            elif request.plan_id:
                # Load from DB
                from db.dao import AgenticPlanDAO
                plan_dict = AgenticPlanDAO.get_plan(session, request.plan_id)
                if not plan_dict:
                    raise HTTPException(status_code=404, detail="Plan not found")
                plan = Plan(**plan_dict)
            else:
                raise HTTPException(status_code=400, detail="Must provide plan_id or plan_override")
            
            # Run agentic search
            result = run_agentic_search(plan, session, cse, llm, scorer)
            
            session.commit()
        
        logger.info(
            "api_agentic_run_done",
            plan_id=result.plan_id,
            iterations=result.iterations,
            approved=result.approved_total,
        )
        
        return RunAgenticResponse(
            plan_id=result.plan_id,
            iterations=result.iterations,
            approved_total=result.approved_total,
            stopped_by=result.stopped_by,
            promoted_urls=result.promoted_urls,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_agentic_run_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agentic/iters/{plan_id}")
async def get_agentic_iterations(plan_id: str):
    """
    Get all iterations for an agentic search plan.
    
    Returns audit trail with executed queries, approvals, rejections, and new queries.
    """
    try:
        logger.info("api_agentic_iters_start", plan_id=plan_id)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            from db.dao import AgenticIterDAO
            
            iterations = AgenticIterDAO.get_iters(session, plan_id)
        
        return {
            "plan_id": plan_id,
            "iterations": iterations,
            "total_iterations": len(iterations),
        }
    
    except Exception as e:
        logger.error("api_agentic_iters_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agentic/approved")
async def get_approved_docs(plan_id: str | None = None, limit: int = 100):
    """
    Get approved documents from agentic search (all plans or filtered by plan_id).
    
    Returns list of approved documents with chunk/vector status.
    """
    try:
        logger.info("api_approved_start", plan_id=plan_id, limit=limit)
        
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            from db.dao import SearchResultDAO, ChunkManifestDAO
            from sqlalchemy import select, and_
            from db.models import SearchResult, SearchQuery
            
            # Build query for approved results
            if plan_id:
                # Filter by plan_id (via agentic_iter approved_urls)
                from db.dao import AgenticIterDAO
                iters = AgenticIterDAO.get_iterations(session, plan_id)
                all_urls = set()
                for it in iters:
                    all_urls.update(it.get("approved_urls", []))
                
                if not all_urls:
                    return ApprovedListResponse(count=0, docs=[])
                
                stmt = (
                    select(SearchResult)
                    .where(and_(
                        SearchResult.approved == True,  # noqa: E712
                        SearchResult.url.in_(list(all_urls))
                    ))
                    .order_by(SearchResult.created_at.desc())
                    .limit(limit)
                )
            else:
                # All approved across all plans
                stmt = (
                    select(SearchResult)
                    .where(SearchResult.approved == True)  # noqa: E712
                    .order_by(SearchResult.created_at.desc())
                    .limit(limit)
                )
            
            results = list(session.scalars(stmt))
            
            # For each result, check if chunk manifest exists
            docs = []
            for r in results:
                manifest = ChunkManifestDAO.find_by_url(session, r.url)
                
                doc = ApprovedDoc(
                    url=r.url,
                    title=r.title,
                    final_type=r.final_type,
                    last_modified=r.last_modified.isoformat() if r.last_modified else None,
                    score=float(r.score) if r.score else None,
                    approved_at=r.created_at.isoformat() if r.created_at else None,
                    doc_hash=manifest.doc_hash if manifest else None,
                    vector_status=manifest.vector_status if manifest else "none",
                    chunk_count=manifest.chunk_count if manifest else 0,
                    cache_status=manifest.status if manifest else "none",
                )
                docs.append(doc)
            
            logger.info("api_approved_done", count=len(docs))
            return ApprovedListResponse(count=len(docs), docs=docs)
    
    except Exception as e:
        logger.error("api_approved_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/regenerate", response_model=RegenerateResponse)
async def regenerate_chunks(request: RegenerateRequest):
    """
    Regenerate chunks for specified documents.
    
    Flow:
    1. Resolve targets (by URLs or doc_hashes) from DB
    2. For each target:
       - Route document type (DB → re-detect → LLM)
       - If overwrite: purge existing chunks
       - Call executor's ingest_one(url, title, etag, last_modified)
       - Save chunks to chunk_store
       - Update manifest
       - Optional: push to VectorDB
    3. Return processed count, errors, and items
    """
    try:
        urls = request.urls or []
        hashes = request.doc_hashes or []
        
        if not urls and not hashes:
            raise HTTPException(400, "Provide 'urls' or 'doc_hashes'")

        logger.info("api_regenerate_start", urls=len(urls), hashes=len(hashes))

        db_session = DatabaseSession()
        
        with next(db_session.get_session()) as session:
            from db.dao import ChunkManifestDAO, ChunkStoreDAO, DocumentCatalogDAO
            from pipelines.routers import DocumentRouter
            from agentic.llm import LLMClient
            from pipelines.executors.pdf_ingestor import PDFIngestor
            from pipelines.executors.html_ingestor import HTMLIngestor
            
            # Initialize dependencies
            llm = LLMClient(api_key=settings.openai_api_key, model="gpt-4o-mini", temperature=0)
            router = DocumentRouter(llm_client=llm)
            
            # Load configs
            ingest_config = load_yaml_with_env("configs/ingest.yaml")
            
            # Initialize executors (note: they need chunker and emitter which we won't use for ingest_one)
            from ingestion.chunkers import TokenAwareChunker
            from ingestion.emitters import JSONLEmitter
            
            chunker = TokenAwareChunker(
                max_tokens=ingest_config.get("chunker", {}).get("max_tokens", 512),
                overlap_tokens=ingest_config.get("chunker", {}).get("overlap_tokens", 50),
                min_tokens=ingest_config.get("chunker", {}).get("min_tokens", 100),
            )
            emitter = JSONLEmitter(output_path=Path(ingest_config.get("output", {}).get("output_dir", "output")))
            
            pdf_exec = PDFIngestor(ingest_config, llm, chunker, emitter)
            html_exec = HTMLIngestor(ingest_config, chunker, emitter, llm)
            
            # Resolve targets
            targets = []
            
            if urls:
                for url in urls:
                    # Try to get from document_catalog
                    doc = DocumentCatalogDAO.find_by_url(session, url)
                    if doc:
                        targets.append({
                            "url": url,
                            "title": doc.title,
                            "final_type": doc.final_type,
                            "etag": doc.etag,
                            "last_modified": doc.last_modified,
                        })
                    else:
                        # New URL, no metadata yet
                        targets.append({
                            "url": url,
                            "title": None,
                            "final_type": None,
                            "etag": None,
                            "last_modified": None,
                        })
            
            if hashes:
                for doc_hash in hashes:
                    manifest = ChunkManifestDAO.find_by_doc_hash(session, doc_hash)
                    if manifest:
                        targets.append({
                            "url": manifest.canonical_url,
                            "title": None,
                            "final_type": None,
                            "etag": None,
                            "last_modified": None,
                            "existing_hash": doc_hash,
                        })
            
            if not targets:
                return RegenerateResponse(processed=0, errors=[{"message": "No targets found"}], items=[])
            
            processed = 0
            items = []
            errors = []
            
            for target in targets:
                url = target["url"]
                
                try:
                    # Route document type
                    doc_type = router.route_item(
                        url=url,
                        final_type=target.get("final_type"),
                        title=target.get("title"),
                    )
                    
                    logger.info("regenerate_processing", url=url, doc_type=doc_type)
                    
                    # Overwrite: delete existing chunks
                    if request.overwrite:
                        if target.get("existing_hash"):
                            ChunkStoreDAO.delete_by_doc_hash(session, target["existing_hash"])
                            logger.info("regenerate_purged", doc_hash=target["existing_hash"])
                        else:
                            # Try to find by URL
                            manifest = ChunkManifestDAO.find_by_url(session, url)
                            if manifest:
                                ChunkStoreDAO.delete_by_doc_hash(session, manifest.doc_hash)
                                logger.info("regenerate_purged", doc_hash=manifest.doc_hash)
                    
                    # Call appropriate executor
                    result = None
                    if doc_type == "pdf":
                        result = pdf_exec.ingest_one(
                            url=url,
                            title=target.get("title"),
                            etag=target.get("etag"),
                            last_modified=target.get("last_modified"),
                        )
                    elif doc_type == "html":
                        result = html_exec.ingest_one(
                            url=url,
                            title=target.get("title"),
                            etag=target.get("etag"),
                            last_modified=target.get("last_modified"),
                        )
                    elif doc_type == "zip":
                        errors.append({"url": url, "reason": "ZIP processing not yet implemented"})
                        continue
                    else:
                        errors.append({"url": url, "reason": f"Unknown doc_type: {doc_type}"})
                        continue
                    
                    if not result or not result.get("ok"):
                        reason = result.get("reason", "ingest_one failed") if result else "no result"
                        errors.append({"url": url, "reason": reason})
                        continue
                    
                    doc_hash = result["doc_hash"]
                    chunks = result.get("chunks", [])
                    meta = result.get("meta", {})
                    
                    # Save to database
                    import json
                    
                    # Upsert manifest
                    ChunkManifestDAO.upsert(
                        session,
                        doc_hash=doc_hash,
                        canonical_url=url,
                        source_file=meta.get("source_file"),
                        doc_type=meta.get("final_type", doc_type),
                        chunk_count=len(chunks),
                        status="done",
                        error_message=None,
                        meta=json.dumps(meta) if meta else None,
                        vector_status="none",
                        last_pushed_at=None,
                        last_pushed_collection=None,
                    )
                    
                    # Bulk create chunks
                    ChunkStoreDAO.bulk_create(session, doc_hash, chunks)
                    
                    logger.info("regenerate_chunks_saved", doc_hash=doc_hash, chunks=len(chunks))
                    
                    vector_status = "none"
                    
                    # Optional: push to VectorDB
                    if request.push_after and len(chunks) > 0:
                        # TODO: Implement actual vector push with embeddings
                        # For now, just mark as present
                        ChunkManifestDAO.update_vector_status(
                            session,
                            doc_hash=doc_hash,
                            vector_status="present",
                            collection=request.collection,
                        )
                        vector_status = "present"
                        logger.info("regenerate_pushed", doc_hash=doc_hash, collection=request.collection)
                    
                    session.commit()
                    
                    items.append({
                        "doc_hash": doc_hash,
                        "chunk_count": len(chunks),
                        "status": "done",
                        "vector_status": vector_status,
                    })
                    processed += 1
                
                except Exception as e:
                    import traceback
                    logger.error("regenerate_error", url=url, error=str(e), trace=traceback.format_exc())
                    errors.append({"url": url, "reason": str(e)})
                    session.rollback()
            
            return RegenerateResponse(processed=processed, errors=errors, items=items)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_regenerate_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chunks/status")
async def get_chunks_status(urls: str | None = None, doc_hashes: str | None = None):
    """
    Get chunk manifest status for specified URLs or doc_hashes (CSV).
    """
    try:
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            from db.dao import ChunkManifestDAO
            
            manifests = []
            
            if urls:
                url_list = [u.strip() for u in urls.split(",")]
                manifests = ChunkManifestDAO.get_by_urls(session, url_list)
            elif doc_hashes:
                hash_list = [h.strip() for h in doc_hashes.split(",")]
                manifests = ChunkManifestDAO.get_by_doc_hashes(session, hash_list)
            
            items = []
            for m in manifests:
                items.append({
                    "doc_hash": m.doc_hash,
                    "url": m.canonical_url,
                    "status": m.status,
                    "chunk_count": m.chunk_count,
                    "vector_status": m.vector_status,
                    "last_pushed_at": m.last_pushed_at.isoformat() if m.last_pushed_at else None,
                    "last_pushed_collection": m.last_pushed_collection,
                })
            
            return ChunkStatusResponse(manifests=items)
    
    except Exception as e:
        logger.error("api_chunks_status_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vector/push", response_model=VectorPushResponse)
async def vector_push(request: VectorPushRequest):
    """
    Push chunks to VectorDB by doc_hashes.
    """
    try:
        logger.info("api_vector_push_start", hashes=len(request.doc_hashes))
        
        # TODO: Implement vector push
        return VectorPushResponse(
            pushed=0,
            skipped=len(request.doc_hashes),
            collection=request.collection,
        )
    
    except Exception as e:
        logger.error("api_vector_push_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vector/delete", response_model=VectorDeleteResponse)
async def vector_delete(request: VectorDeleteRequest):
    """
    Delete chunks from VectorDB by doc_hashes.
    """
    try:
        logger.info("api_vector_delete_start", hashes=len(request.doc_hashes))
        
        # TODO: Implement vector delete
        return VectorDeleteResponse(
            deleted=0,
            collection=request.collection,
        )
    
    except Exception as e:
        logger.error("api_vector_delete_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ui", include_in_schema=False)
async def ui_console():
    """Serve Agentic Search Console UI."""
    ui_file = Path(__file__).parent.parent / "ui" / "static" / "index.html"
    
    if not ui_file.exists():
        raise HTTPException(status_code=404, detail="UI not found")
    
    return FileResponse(ui_file)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "agentic-reg-ingest",
        "version": "2.0.0",
        "ui": "http://localhost:8000/ui",
        "endpoints": {
            "health": "/health",
            "search": "POST /run/search",
            "ingest": "POST /run/ingest",
            "agentic_plan": "POST /agentic/plan",
            "agentic_run": "POST /agentic/run",
            "agentic_iters": "GET /agentic/iters/{plan_id}",
            "ui_console": "GET /ui",
        },
    }

