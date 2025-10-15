# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

-- Migration: Create chunk_manifest and chunk_store tables
-- Date: 2025-10-14
-- Purpose: Track chunked documents and store their chunks for vector loading

-- Table: chunk_manifest
-- Manifest for chunked documents with processing status
CREATE TABLE IF NOT EXISTS chunk_manifest (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doc_hash VARCHAR(64) NOT NULL UNIQUE,
    canonical_url VARCHAR(2048) NOT NULL,
    source_file VARCHAR(512) NULL,
    doc_type VARCHAR(50) NULL,
    chunk_count INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'queued' COMMENT 'queued|processing|done|error',
    error_message TEXT NULL,
    meta TEXT NULL COMMENT 'JSON string with metadata',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Vector push tracking
    last_pushed_at TIMESTAMP NULL COMMENT 'Last time chunks were pushed to VectorDB',
    last_pushed_collection VARCHAR(128) NULL COMMENT 'Collection name where chunks were pushed',
    vector_status ENUM('none','present','partial','error') NOT NULL DEFAULT 'none' 
        COMMENT 'none=not pushed, present=all in vector, partial=some in vector, error=push failed',
    
    INDEX idx_doc_hash (doc_hash),
    INDEX idx_status (status),
    INDEX ix_manifest_status (status, vector_status),
    INDEX idx_canonical_url (canonical_url(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: chunk_store
-- Stores individual chunks with embeddings metadata
CREATE TABLE IF NOT EXISTS chunk_store (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doc_hash VARCHAR(64) NOT NULL,
    chunk_id VARCHAR(128) NOT NULL COMMENT 'Unique chunk identifier within document',
    chunk_index INT NOT NULL COMMENT 'Sequential index of chunk in document',
    text_content TEXT NOT NULL,
    tokens INT NULL,
    anchors TEXT NULL COMMENT 'JSON array of anchor objects',
    chunk_metadata TEXT NULL COMMENT 'JSON object with chunk metadata (renamed from metadata to avoid SQLAlchemy reserved word)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uq_doc_chunk (doc_hash, chunk_id),
    INDEX idx_doc_hash (doc_hash),
    INDEX idx_chunk_index (doc_hash, chunk_index),
    FOREIGN KEY (doc_hash) REFERENCES chunk_manifest(doc_hash) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

