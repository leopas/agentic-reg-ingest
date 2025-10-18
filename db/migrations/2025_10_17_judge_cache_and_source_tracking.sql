-- SPDX-License-Identifier: MIT
-- Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

-- Judge cache table and source pipeline tracking
-- Migration: 2025-10-17

-- Create judge_cache table
CREATE TABLE IF NOT EXISTS judge_cache (
    url_hash VARCHAR(64) PRIMARY KEY,
    url VARCHAR(2048) NOT NULL,
    decision ENUM('approved', 'rejected') NOT NULL,
    reason TEXT,
    violations TEXT,
    plan_goal_hash VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    
    INDEX idx_plan_goal_hash (plan_goal_hash),
    INDEX idx_expires_at (expires_at),
    INDEX idx_url_goal (url_hash, plan_goal_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add source_pipeline tracking to chunk_manifest
ALTER TABLE chunk_manifest 
ADD COLUMN source_pipeline ENUM('regular', 'enrichment', 'manual') DEFAULT 'regular' NOT NULL;

-- Create index for filtering by source
CREATE INDEX idx_source_pipeline ON chunk_manifest(source_pipeline);

