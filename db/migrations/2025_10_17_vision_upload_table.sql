-- SPDX-License-Identifier: MIT
-- Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

-- Vision Upload table for enrichment pipeline
-- Migration: 2025-10-17

CREATE TABLE IF NOT EXISTS vision_upload (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    upload_id VARCHAR(64) NOT NULL UNIQUE,
    original_filename VARCHAR(512) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(128),
    
    -- Pipeline status
    status ENUM('uploaded', 'processing', 'awaiting_review', 'completed', 'failed') NOT NULL DEFAULT 'uploaded',
    
    -- Stage tracking
    stage_ocr VARCHAR(50) DEFAULT 'pending',
    stage_multimodal VARCHAR(50) DEFAULT 'pending',
    stage_allowlist VARCHAR(50) DEFAULT 'pending',
    stage_agentic VARCHAR(50) DEFAULT 'pending',
    stage_scrape VARCHAR(50) DEFAULT 'pending',
    stage_vector VARCHAR(50) DEFAULT 'pending',
    
    -- Output artifacts
    jsonl_path VARCHAR(1024),
    txt_output_dir VARCHAR(1024),
    plan_id VARCHAR(64),
    
    -- Metadata
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME,
    
    INDEX idx_upload_id (upload_id),
    INDEX idx_file_hash (file_hash),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

