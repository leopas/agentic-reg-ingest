# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""SQLAlchemy ORM models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class SearchQuery(Base):
    """Search query cache table."""
    
    __tablename__ = "search_query"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cache_key = Column(String(64), nullable=False, unique=True, index=True)
    cx = Column(String(255), nullable=False)
    query_text = Column(Text, nullable=False)
    allow_domains = Column(Text, nullable=True)
    top_n = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    result_count = Column(Integer, default=0)
    
    # Relationship
    results = relationship("SearchResult", back_populates="query", cascade="all, delete-orphan")


class SearchResult(Base):
    """Individual search result."""
    
    __tablename__ = "search_result"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    query_id = Column(BigInteger, ForeignKey("search_query.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    rank_position = Column(Integer, nullable=False)
    score = Column(Numeric(5, 4), nullable=True)
    content_type = Column(String(100), nullable=True)
    
    # Typing detection columns (added 2025-10-14)
    http_content_type = Column(String(128), nullable=True)
    http_content_disposition = Column(String(255), nullable=True)
    url_ext = Column(String(16), nullable=True)
    detected_mime = Column(String(128), nullable=True)
    detected_ext = Column(String(16), nullable=True)
    final_type = Column(Enum('pdf', 'zip', 'html', 'unknown', name='final_type_enum'), default='unknown', index=True)
    fetch_status = Column(Enum('ok', 'redirected', 'blocked', 'error', name='fetch_status_enum'), nullable=True, index=True)
    
    last_modified = Column(DateTime, nullable=True)
    approved = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    query = relationship("SearchQuery", back_populates="results")


class DocumentCatalog(Base):
    """Canonical document catalog for diff detection."""
    
    __tablename__ = "document_catalog"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    canonical_url = Column(String(2048), nullable=False, unique=True)
    content_type = Column(String(100), nullable=True)
    final_type = Column(Enum('pdf', 'zip', 'html', 'unknown', name='doc_final_type_enum'), default='unknown', index=True)
    last_modified = Column(DateTime, nullable=True)
    etag = Column(String(255), nullable=True)
    content_hash = Column(String(64), nullable=True)
    title = Column(Text, nullable=True)
    domain = Column(String(255), nullable=True, index=True)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_checked_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_ingested_at = Column(DateTime, nullable=True)
    ingest_status = Column(String(50), default="pending", index=True)
    error_message = Column(Text, nullable=True)


class ChunkManifest(Base):
    """Manifest for chunked documents with vector push tracking."""
    
    __tablename__ = "chunk_manifest"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_hash = Column(String(64), nullable=False, unique=True, index=True)
    canonical_url = Column(String(2048), nullable=False)
    source_file = Column(String(512), nullable=True)
    doc_type = Column(String(50), nullable=True)
    chunk_count = Column(Integer, default=0)
    status = Column(String(50), default="queued", index=True)
    error_message = Column(Text, nullable=True)
    meta = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Vector push tracking (added 2025-10-14)
    last_pushed_at = Column(DateTime, nullable=True)
    last_pushed_collection = Column(String(128), nullable=True)
    vector_status = Column(
        Enum('none', 'present', 'partial', 'error', name='vector_status_enum'),
        default='none',
        nullable=False
    )
    
    # Relationship
    chunks = relationship("ChunkStore", back_populates="manifest", cascade="all, delete-orphan")


class ChunkStore(Base):
    """Individual chunks with content and metadata."""
    
    __tablename__ = "chunk_store"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_hash = Column(String(64), ForeignKey("chunk_manifest.doc_hash", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String(128), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    tokens = Column(Integer, nullable=True)
    anchors = Column(Text, nullable=True)  # JSON array
    chunk_metadata = Column(Text, nullable=True)  # JSON object (renamed from 'metadata' to avoid SQLAlchemy reserved name)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    manifest = relationship("ChunkManifest", back_populates="chunks")

