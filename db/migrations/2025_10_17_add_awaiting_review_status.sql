-- SPDX-License-Identifier: MIT
-- Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

-- Add 'awaiting_review' status to vision_upload table
-- Migration: 2025-10-17

ALTER TABLE vision_upload 
MODIFY COLUMN status ENUM('uploaded', 'processing', 'awaiting_review', 'completed', 'failed') 
NOT NULL DEFAULT 'uploaded';

