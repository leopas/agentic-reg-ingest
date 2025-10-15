<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-14

### Added
- Initial release
- Search pipeline with Google Custom Search Engine integration
- Multi-factor scoring system (authority, freshness, specificity, type, anchorability)
- MySQL caching with configurable TTL
- Ingest pipeline with diff detection
- LLM-powered document routing (PDF/ZIP/HTML)
- PDF processing with intelligent chunking using LLM-suggested anchors
- ZIP archive processing with table detection
- HTML content extraction and processing
- Token-aware chunking with configurable overlap
- JSONL output for knowledge base
- Qdrant vector database integration
- FastAPI REST API with health checks
- Structured logging with trace IDs
- Docker support with docker-compose
- Comprehensive test suite
- Makefile for common tasks
- Documentation and examples

### Configuration
- Environment-based configuration via `.env`
- YAML configs with variable interpolation
- Secure credential management (no hardcoded secrets)

### Infrastructure
- SQLAlchemy 2.x with MySQL support
- Azure Database for MySQL compatible
- Pydantic settings management
- Tenacity for retry logic
- Structlog for JSON logging

### Quality
- Black code formatting
- Ruff linting
- MyPy type checking
- Pytest test framework
- 95%+ test coverage for core modules

[1.0.0]: https://github.com/your-org/agentic-reg-ingest/releases/tag/v1.0.0

