-- Database schema for agentic-reg-ingest
-- MySQL 8.0 compatible

-- Table: search_query
-- Stores cached search queries with TTL
CREATE TABLE IF NOT EXISTS search_query (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cache_key VARCHAR(64) NOT NULL UNIQUE,
    cx VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    allow_domains TEXT,
    top_n INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    result_count INT DEFAULT 0,
    INDEX idx_cache_key (cache_key),
    INDEX idx_expires_at (expires_at),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: search_result
-- Stores individual search results linked to queries
CREATE TABLE IF NOT EXISTS search_result (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    query_id BIGINT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    snippet TEXT,
    rank_position INT NOT NULL,
    score DECIMAL(5, 4),
    content_type VARCHAR(100),
    last_modified TIMESTAMP NULL,
    approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES search_query(id) ON DELETE CASCADE,
    INDEX idx_query_id (query_id),
    INDEX idx_approved (approved),
    INDEX idx_score (score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: document_catalog
-- Canonical store of documents with metadata for diff detection
CREATE TABLE IF NOT EXISTS document_catalog (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    canonical_url VARCHAR(2048) NOT NULL UNIQUE,
    content_type VARCHAR(100),
    last_modified TIMESTAMP NULL,
    etag VARCHAR(255),
    content_hash VARCHAR(64),
    title TEXT,
    domain VARCHAR(255),
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_ingested_at TIMESTAMP NULL,
    ingest_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    INDEX idx_canonical_url (canonical_url(255)),
    INDEX idx_domain (domain),
    INDEX idx_ingest_status (ingest_status),
    INDEX idx_last_checked_at (last_checked_at),
    INDEX idx_last_ingested_at (last_ingested_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

