-- db_aulas.agentic_plan definição

CREATE TABLE `agentic_plan` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `plan_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `goal` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `plan_json` json NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `plan_id` (`plan_id`),
  KEY `idx_plan_id` (`plan_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- db_aulas.chunk_manifest definição

CREATE TABLE `chunk_manifest` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `doc_hash` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `canonical_url` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_file` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `doc_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `chunk_count` int DEFAULT '0',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'queued' COMMENT 'queued|processing|done|error',
  `error_message` text COLLATE utf8mb4_unicode_ci,
  `meta` text COLLATE utf8mb4_unicode_ci COMMENT 'JSON string with metadata',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_pushed_at` timestamp NULL DEFAULT NULL COMMENT 'Last time chunks were pushed to VectorDB',
  `last_pushed_collection` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Collection name where chunks were pushed',
  `vector_status` enum('none','present','partial','error') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'none' COMMENT 'none=not pushed, present=all in vector, partial=some in vector, error=push failed',
  PRIMARY KEY (`id`),
  UNIQUE KEY `doc_hash` (`doc_hash`),
  KEY `idx_doc_hash` (`doc_hash`),
  KEY `idx_status` (`status`),
  KEY `ix_manifest_status` (`status`,`vector_status`),
  KEY `idx_canonical_url` (`canonical_url`(255))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- db_aulas.document_catalog definição

CREATE TABLE `document_catalog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `canonical_url` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `final_type` enum('pdf','zip','html','unknown') COLLATE utf8mb4_unicode_ci DEFAULT 'unknown',
  `last_modified` timestamp NULL DEFAULT NULL,
  `etag` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content_hash` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `title` text COLLATE utf8mb4_unicode_ci,
  `domain` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `first_seen_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_checked_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_ingested_at` timestamp NULL DEFAULT NULL,
  `ingest_status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `error_message` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_canonical_url_unique` (`canonical_url`(191)),
  KEY `idx_domain` (`domain`),
  KEY `idx_ingest_status` (`ingest_status`),
  KEY `idx_last_checked_at` (`last_checked_at`),
  KEY `idx_last_ingested_at` (`last_ingested_at`),
  KEY `idx_doc_final_type` (`final_type`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- db_aulas.search_query definição

CREATE TABLE `search_query` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cache_key` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cx` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `query_text` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `allow_domains` text COLLATE utf8mb4_unicode_ci,
  `top_n` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` timestamp NOT NULL,
  `result_count` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `cache_key` (`cache_key`),
  KEY `idx_cache_key` (`cache_key`),
  KEY `idx_expires_at` (`expires_at`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- db_aulas.agentic_iter definição

CREATE TABLE `agentic_iter` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `plan_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `iter_num` int NOT NULL,
  `executed_queries` json NOT NULL,
  `approved_urls` json NOT NULL,
  `rejected_json` json NOT NULL,
  `new_queries` json NOT NULL,
  `summary` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_plan_iter` (`plan_id`,`iter_num`),
  KEY `idx_plan_id` (`plan_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `agentic_iter_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `agentic_plan` (`plan_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- db_aulas.chunk_store definição

CREATE TABLE `chunk_store` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `doc_hash` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `chunk_id` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Unique chunk identifier within document',
  `chunk_index` int NOT NULL COMMENT 'Sequential index of chunk in document',
  `text_content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `tokens` int DEFAULT NULL,
  `anchors` text COLLATE utf8mb4_unicode_ci COMMENT 'JSON array of anchor objects',
  `chunk_metadata` text COLLATE utf8mb4_unicode_ci COMMENT 'JSON object with chunk metadata (renamed from metadata to avoid SQLAlchemy reserved word)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_doc_chunk` (`doc_hash`,`chunk_id`),
  KEY `idx_doc_hash` (`doc_hash`),
  KEY `idx_chunk_index` (`doc_hash`,`chunk_index`),
  CONSTRAINT `chunk_store_ibfk_1` FOREIGN KEY (`doc_hash`) REFERENCES `chunk_manifest` (`doc_hash`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=981 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- db_aulas.search_result definição

CREATE TABLE `search_result` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `query_id` bigint NOT NULL,
  `url` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` text COLLATE utf8mb4_unicode_ci,
  `snippet` text COLLATE utf8mb4_unicode_ci,
  `rank_position` int NOT NULL,
  `score` decimal(5,4) DEFAULT NULL,
  `content_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `http_content_type` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `http_content_disposition` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url_ext` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `detected_mime` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `detected_ext` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `final_type` enum('pdf','zip','html','unknown') COLLATE utf8mb4_unicode_ci DEFAULT 'unknown',
  `fetch_status` enum('ok','redirected','blocked','error') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_modified` timestamp NULL DEFAULT NULL,
  `approved` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_query_id` (`query_id`),
  KEY `idx_approved` (`approved`),
  KEY `idx_score` (`score` DESC),
  KEY `idx_final_type` (`final_type`),
  KEY `idx_fetch_status` (`fetch_status`),
  CONSTRAINT `search_result_ibfk_1` FOREIGN KEY (`query_id`) REFERENCES `search_query` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;