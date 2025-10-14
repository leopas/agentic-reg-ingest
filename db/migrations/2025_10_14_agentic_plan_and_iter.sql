-- Migration: Add agentic search plan and iteration tracking
-- Date: 2025-10-14
-- Purpose: Enable Plan→Act→Observe→Judge→Re-plan loop with full audit trail

-- Table: agentic_plan
-- Stores search plans with goals, queries, and quality gates
CREATE TABLE IF NOT EXISTS agentic_plan (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  plan_id CHAR(36) NOT NULL UNIQUE,
  goal TEXT NOT NULL,
  plan_json JSON NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_plan_id (plan_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: agentic_iter
-- Stores iteration results for full audit trail
CREATE TABLE IF NOT EXISTS agentic_iter (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  plan_id CHAR(36) NOT NULL,
  iter_num INT NOT NULL,
  executed_queries JSON NOT NULL,
  approved_urls JSON NOT NULL,
  rejected_json JSON NOT NULL,
  new_queries JSON NOT NULL,
  summary TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_plan_iter (plan_id, iter_num),
  INDEX idx_plan_id (plan_id),
  INDEX idx_created_at (created_at),
  FOREIGN KEY (plan_id) REFERENCES agentic_plan(plan_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

