# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

-- Migration: Add typing columns to search_result and document_catalog tables
-- Date: 2025-10-14
-- Purpose: Robust document type detection and routing

-- Add new typing columns to search_result table
ALTER TABLE search_result
  ADD COLUMN http_content_type VARCHAR(128) NULL AFTER content_type,
  ADD COLUMN http_content_disposition VARCHAR(255) NULL AFTER http_content_type,
  ADD COLUMN url_ext VARCHAR(16) NULL AFTER http_content_disposition,
  ADD COLUMN detected_mime VARCHAR(128) NULL AFTER url_ext,
  ADD COLUMN detected_ext VARCHAR(16) NULL AFTER detected_mime,
  ADD COLUMN final_type ENUM('pdf','zip','html','unknown') DEFAULT 'unknown' AFTER detected_ext,
  ADD COLUMN fetch_status ENUM('ok','redirected','blocked','error') DEFAULT NULL AFTER final_type;

-- Add index on final_type for faster filtering
CREATE INDEX idx_final_type ON search_result(final_type);

-- Add index on fetch_status for monitoring
CREATE INDEX idx_fetch_status ON search_result(fetch_status);

-- Add final_type to document_catalog for routing at ingest time
ALTER TABLE document_catalog
  ADD COLUMN final_type ENUM('pdf','zip','html','unknown') DEFAULT 'unknown' AFTER content_type;

-- Add index on final_type
CREATE INDEX idx_doc_final_type ON document_catalog(final_type);

