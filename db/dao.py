"""Data Access Objects for database operations."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from db.models import ChunkManifest, ChunkStore, DocumentCatalog, SearchQuery, SearchResult


class SearchQueryDAO:
    """DAO for SearchQuery operations."""
    
    @staticmethod
    def find_by_cache_key(session: Session, cache_key: str) -> Optional[SearchQuery]:
        """Find search query by cache key."""
        stmt = select(SearchQuery).where(SearchQuery.cache_key == cache_key)
        return session.scalar(stmt)
    
    @staticmethod
    def is_cache_valid(query: SearchQuery) -> bool:
        """Check if cache is still valid (not expired)."""
        return query.expires_at > datetime.utcnow()
    
    @staticmethod
    def create(
        session: Session,
        cache_key: str,
        cx: str,
        query_text: str,
        allow_domains: Optional[str],
        top_n: int,
        ttl_days: int,
    ) -> SearchQuery:
        """Create new search query record."""
        query = SearchQuery(
            cache_key=cache_key,
            cx=cx,
            query_text=query_text,
            allow_domains=allow_domains,
            top_n=top_n,
            expires_at=datetime.utcnow() + timedelta(days=ttl_days),
        )
        session.add(query)
        session.flush()
        return query


class SearchResultDAO:
    """DAO for SearchResult operations."""
    
    @staticmethod
    def get_approved_results(session: Session, query_id: int) -> List[SearchResult]:
        """Get approved results for a query."""
        stmt = (
            select(SearchResult)
            .where(SearchResult.query_id == query_id)
            .where(SearchResult.approved == True)  # noqa: E712
            .order_by(SearchResult.rank_position)
        )
        return list(session.scalars(stmt))
    
    @staticmethod
    def create(
        session: Session,
        query_id: int,
        url: str,
        title: Optional[str],
        snippet: Optional[str],
        rank_position: int,
        score: Optional[float],
        content_type: Optional[str],
        last_modified: Optional[datetime],
        approved: bool = True,
        # Typing detection fields (added 2025-10-14)
        http_content_type: Optional[str] = None,
        http_content_disposition: Optional[str] = None,
        url_ext: Optional[str] = None,
        detected_mime: Optional[str] = None,
        detected_ext: Optional[str] = None,
        final_type: str = "unknown",
        fetch_status: Optional[str] = None,
    ) -> SearchResult:
        """Create new search result with typing information."""
        result = SearchResult(
            query_id=query_id,
            url=url,
            title=title,
            snippet=snippet,
            rank_position=rank_position,
            score=score,
            content_type=content_type,
            last_modified=last_modified,
            approved=approved,
            # Typing fields
            http_content_type=http_content_type,
            http_content_disposition=http_content_disposition,
            url_ext=url_ext,
            detected_mime=detected_mime,
            detected_ext=detected_ext,
            final_type=final_type,
            fetch_status=fetch_status,
        )
        session.add(result)
        session.flush()
        return result
    
    @staticmethod
    def update_typing(
        session: Session,
        result_id: int,
        http_content_type: Optional[str] = None,
        http_content_disposition: Optional[str] = None,
        url_ext: Optional[str] = None,
        detected_mime: Optional[str] = None,
        detected_ext: Optional[str] = None,
        final_type: Optional[str] = None,
        fetch_status: Optional[str] = None,
    ) -> None:
        """Update typing information for an existing result."""
        stmt = select(SearchResult).where(SearchResult.id == result_id)
        result = session.scalar(stmt)
        
        if result:
            if http_content_type is not None:
                result.http_content_type = http_content_type
            if http_content_disposition is not None:
                result.http_content_disposition = http_content_disposition
            if url_ext is not None:
                result.url_ext = url_ext
            if detected_mime is not None:
                result.detected_mime = detected_mime
            if detected_ext is not None:
                result.detected_ext = detected_ext
            if final_type is not None:
                result.final_type = final_type
            if fetch_status is not None:
                result.fetch_status = fetch_status
            session.flush()


class DocumentCatalogDAO:
    """DAO for DocumentCatalog operations."""
    
    @staticmethod
    def find_by_url(session: Session, canonical_url: str) -> Optional[DocumentCatalog]:
        """Find document by canonical URL."""
        stmt = select(DocumentCatalog).where(DocumentCatalog.canonical_url == canonical_url)
        return session.scalar(stmt)
    
    @staticmethod
    def upsert(
        session: Session,
        canonical_url: str,
        content_type: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        etag: Optional[str] = None,
        title: Optional[str] = None,
        domain: Optional[str] = None,
        final_type: Optional[str] = None,
    ) -> DocumentCatalog:
        """Insert or update document catalog entry."""
        doc = DocumentCatalogDAO.find_by_url(session, canonical_url)
        
        if doc:
            # Update existing
            if content_type is not None:
                doc.content_type = content_type
            if last_modified is not None:
                doc.last_modified = last_modified
            if etag is not None:
                doc.etag = etag
            if title is not None:
                doc.title = title
            if domain is not None:
                doc.domain = domain
            if final_type is not None:
                doc.final_type = final_type
            doc.last_checked_at = datetime.utcnow()
        else:
            # Create new
            doc = DocumentCatalog(
                canonical_url=canonical_url,
                content_type=content_type,
                last_modified=last_modified,
                etag=etag,
                title=title,
                domain=domain,
                final_type=final_type or "unknown",
            )
            session.add(doc)
        
        session.flush()
        return doc
    
    @staticmethod
    def mark_ingested(
        session: Session,
        canonical_url: str,
        status: str = "completed",
        error_message: Optional[str] = None,
    ) -> None:
        """Mark document as ingested."""
        doc = DocumentCatalogDAO.find_by_url(session, canonical_url)
        if doc:
            doc.ingest_status = status
            doc.last_ingested_at = datetime.utcnow()
            if error_message:
                doc.error_message = error_message
            session.flush()
    
    @staticmethod
    def get_pending_or_changed(session: Session, limit: Optional[int] = None) -> List[DocumentCatalog]:
        """Get documents pending ingestion or that need re-ingestion."""
        stmt = (
            select(DocumentCatalog)
            .where(
                (DocumentCatalog.ingest_status.in_(["pending", "failed"]))
                | (DocumentCatalog.last_modified > DocumentCatalog.last_ingested_at)
            )
            .order_by(DocumentCatalog.last_checked_at.desc())
        )
        
        if limit:
            stmt = stmt.limit(limit)
        
        return list(session.scalars(stmt))


class AgenticPlanDAO:
    """DAO for Agentic Search plans."""
    
    @staticmethod
    def save_plan(
        session: Session,
        plan_id: str,
        goal: str,
        plan_json: Dict[str, Any],
    ) -> None:
        """
        Save agentic search plan.
        
        Args:
            session: DB session
            plan_id: UUID for plan
            goal: Search goal/objective
            plan_json: Full plan as dict
        """
        import json
        from sqlalchemy import text
        
        stmt = text("""
            INSERT INTO agentic_plan (plan_id, goal, plan_json)
            VALUES (:plan_id, :goal, :plan_json)
            ON DUPLICATE KEY UPDATE
                goal = :goal,
                plan_json = :plan_json,
                updated_at = CURRENT_TIMESTAMP
        """)
        
        session.execute(stmt, {
            "plan_id": plan_id,
            "goal": goal,
            "plan_json": json.dumps(plan_json, ensure_ascii=False),
        })
        session.flush()
    
    @staticmethod
    def get_plan(session: Session, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID."""
        import json
        from sqlalchemy import text
        
        stmt = text("SELECT plan_json FROM agentic_plan WHERE plan_id = :plan_id")
        result = session.execute(stmt, {"plan_id": plan_id}).fetchone()
        
        if result:
            return json.loads(result[0])
        return None


class AgenticIterDAO:
    """DAO for Agentic Search iterations."""
    
    @staticmethod
    def save_iter(
        session: Session,
        plan_id: str,
        iter_num: int,
        executed_queries: List[str],
        approved_urls: List[str],
        rejected_json: List[Dict[str, Any]],
        new_queries: List[str],
        summary: Optional[str] = None,
    ) -> None:
        """
        Save iteration result.
        
        Args:
            session: DB session
            plan_id: Plan UUID
            iter_num: Iteration number
            executed_queries: Queries executed in this iteration
            approved_urls: URLs approved in this iteration
            rejected_json: Rejected candidates with reasons
            new_queries: New queries proposed by judge
            summary: Optional summary text
        """
        import json
        from sqlalchemy import text
        
        stmt = text("""
            INSERT INTO agentic_iter (
                plan_id, iter_num, executed_queries, approved_urls,
                rejected_json, new_queries, summary
            ) VALUES (
                :plan_id, :iter_num, :executed_queries, :approved_urls,
                :rejected_json, :new_queries, :summary
            )
        """)
        
        session.execute(stmt, {
            "plan_id": plan_id,
            "iter_num": iter_num,
            "executed_queries": json.dumps(executed_queries, ensure_ascii=False),
            "approved_urls": json.dumps(approved_urls, ensure_ascii=False),
            "rejected_json": json.dumps(rejected_json, ensure_ascii=False),
            "new_queries": json.dumps(new_queries, ensure_ascii=False),
            "summary": summary,
        })
        session.flush()
    
    @staticmethod
    def get_iters(session: Session, plan_id: str) -> List[Dict[str, Any]]:
        """Get all iterations for a plan."""
        import json
        from sqlalchemy import text
        
        stmt = text("""
            SELECT iter_num, executed_queries, approved_urls,
                   rejected_json, new_queries, summary, created_at
            FROM agentic_iter
            WHERE plan_id = :plan_id
            ORDER BY iter_num ASC
        """)
        
        results = session.execute(stmt, {"plan_id": plan_id}).fetchall()
        
        iterations = []
        for row in results:
            iterations.append({
                "iter_num": row[0],
                "executed_queries": json.loads(row[1]),
                "approved_urls": json.loads(row[2]),
                "rejected": json.loads(row[3]),
                "new_queries": json.loads(row[4]),
                "summary": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
            })
        
        return iterations


class ChunkManifestDAO:
    """DAO for ChunkManifest operations."""
    
    @staticmethod
    def find_by_doc_hash(session: Session, doc_hash: str) -> Optional[ChunkManifest]:
        """Find chunk manifest by doc_hash."""
        stmt = select(ChunkManifest).where(ChunkManifest.doc_hash == doc_hash)
        return session.scalar(stmt)
    
    @staticmethod
    def find_by_url(session: Session, canonical_url: str) -> Optional[ChunkManifest]:
        """Find chunk manifest by canonical URL."""
        stmt = select(ChunkManifest).where(ChunkManifest.canonical_url == canonical_url)
        return session.scalar(stmt)
    
    @staticmethod
    def upsert(
        session: Session,
        doc_hash: str,
        canonical_url: str,
        source_file: Optional[str] = None,
        doc_type: Optional[str] = None,
        chunk_count: int = 0,
        status: str = "queued",
        error_message: Optional[str] = None,
        meta: Optional[str] = None,
        vector_status: str = "none",
        last_pushed_at: Optional[datetime] = None,
        last_pushed_collection: Optional[str] = None,
    ) -> ChunkManifest:
        """Upsert chunk manifest record."""
        manifest = ChunkManifestDAO.find_by_doc_hash(session, doc_hash)
        
        if manifest:
            # Update existing
            manifest.canonical_url = canonical_url
            if source_file is not None:
                manifest.source_file = source_file
            if doc_type is not None:
                manifest.doc_type = doc_type
            manifest.chunk_count = chunk_count
            manifest.status = status
            manifest.error_message = error_message
            if meta is not None:
                manifest.meta = meta
            manifest.vector_status = vector_status
            if last_pushed_at is not None:
                manifest.last_pushed_at = last_pushed_at
            if last_pushed_collection is not None:
                manifest.last_pushed_collection = last_pushed_collection
            manifest.updated_at = datetime.utcnow()
        else:
            # Create new
            manifest = ChunkManifest(
                doc_hash=doc_hash,
                canonical_url=canonical_url,
                source_file=source_file,
                doc_type=doc_type,
                chunk_count=chunk_count,
                status=status,
                error_message=error_message,
                meta=meta,
                vector_status=vector_status,
                last_pushed_at=last_pushed_at,
                last_pushed_collection=last_pushed_collection,
            )
            session.add(manifest)
        
        session.flush()
        return manifest
    
    @staticmethod
    def update_vector_status(
        session: Session,
        doc_hash: str,
        vector_status: str,
        collection: Optional[str] = None,
    ) -> None:
        """Update vector status for a manifest."""
        manifest = ChunkManifestDAO.find_by_doc_hash(session, doc_hash)
        if manifest:
            manifest.vector_status = vector_status
            if vector_status == "present":
                manifest.last_pushed_at = datetime.utcnow()
                if collection:
                    manifest.last_pushed_collection = collection
            elif vector_status == "none":
                manifest.last_pushed_at = None
                manifest.last_pushed_collection = None
            session.flush()
    
    @staticmethod
    def get_by_status(session: Session, status: str, limit: int = 100) -> List[ChunkManifest]:
        """Get manifests by status."""
        stmt = (
            select(ChunkManifest)
            .where(ChunkManifest.status == status)
            .order_by(ChunkManifest.created_at.desc())
            .limit(limit)
        )
        return list(session.scalars(stmt))
    
    @staticmethod
    def get_by_urls(session: Session, urls: List[str]) -> List[ChunkManifest]:
        """Get manifests by URLs."""
        stmt = select(ChunkManifest).where(ChunkManifest.canonical_url.in_(urls))
        return list(session.scalars(stmt))
    
    @staticmethod
    def get_by_doc_hashes(session: Session, doc_hashes: List[str]) -> List[ChunkManifest]:
        """Get manifests by doc_hashes."""
        stmt = select(ChunkManifest).where(ChunkManifest.doc_hash.in_(doc_hashes))
        return list(session.scalars(stmt))


class ChunkStoreDAO:
    """DAO for ChunkStore operations."""
    
    @staticmethod
    def create_chunk(
        session: Session,
        doc_hash: str,
        chunk_id: str,
        chunk_index: int,
        text_content: str,
        tokens: Optional[int] = None,
        anchors: Optional[str] = None,
        chunk_metadata: Optional[str] = None,
    ) -> ChunkStore:
        """Create new chunk record."""
        chunk = ChunkStore(
            doc_hash=doc_hash,
            chunk_id=chunk_id,
            chunk_index=chunk_index,
            text_content=text_content,
            tokens=tokens,
            anchors=anchors,
            chunk_metadata=chunk_metadata,
        )
        session.add(chunk)
        session.flush()
        return chunk
    
    @staticmethod
    def get_chunks_by_doc_hash(session: Session, doc_hash: str) -> List[ChunkStore]:
        """Get all chunks for a document."""
        stmt = (
            select(ChunkStore)
            .where(ChunkStore.doc_hash == doc_hash)
            .order_by(ChunkStore.chunk_index)
        )
        return list(session.scalars(stmt))
    
    @staticmethod
    def delete_by_doc_hash(session: Session, doc_hash: str) -> int:
        """Delete all chunks for a document. Returns count deleted."""
        chunks = ChunkStoreDAO.get_chunks_by_doc_hash(session, doc_hash)
        count = len(chunks)
        for chunk in chunks:
            session.delete(chunk)
        session.flush()
        return count
    
    @staticmethod
    def bulk_create(
        session: Session,
        doc_hash: str,
        chunks: List[Dict[str, Any]],
    ) -> int:
        """Bulk create chunks. Returns count created."""
        for idx, chunk_data in enumerate(chunks):
            ChunkStoreDAO.create_chunk(
                session,
                doc_hash=doc_hash,
                chunk_id=chunk_data.get("chunk_id", f"{doc_hash}:{idx}"),
                chunk_index=idx,
                text_content=chunk_data.get("text", chunk_data.get("text_content", "")),
                tokens=chunk_data.get("tokens"),
                anchors=json.dumps(chunk_data.get("anchors")) if chunk_data.get("anchors") else None,
                chunk_metadata=json.dumps(chunk_data.get("metadata")) if chunk_data.get("metadata") else None,
            )
        session.flush()
        return len(chunks)

