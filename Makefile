.PHONY: help venv deps lock db-init migrate migrate-agentic migrate-chunks search ingest agentic-example agentic-view ui api lint test typecheck clean license-headers

help:
	@echo "Agentic Regulatory Ingest - Make targets"
	@echo ""
	@echo "Setup:"
	@echo "  make venv        - Create virtual environment"
	@echo "  make deps        - Install dependencies"
	@echo "  make lock        - Lock dependencies (requires pip-tools)"
	@echo "  make db-init         - Initialize database schema"
	@echo "  make migrate         - Run typing migrations"
	@echo "  make migrate-agentic - Run agentic search migrations"
	@echo ""
	@echo "Pipelines:"
	@echo "  make search          - Run search pipeline"
	@echo "  make ingest          - Run ingest pipeline"
	@echo "  make agentic-example - Run agentic search (PDFs/ZIPs)"
	@echo "  make agentic-html    - Run agentic search (HTMLs only)"
	@echo "  make agentic-view    - View agentic iterations (set PLAN_ID=...)"
	@echo ""
	@echo "Development:"
	@echo "  make ui          - Start API + open web console"
	@echo "  make api         - Start FastAPI server"
	@echo "  make lint        - Run linters (ruff + black)"
	@echo "  make test        - Run tests"
	@echo "  make typecheck   - Run type checker (mypy)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Clean generated files"

venv:
	python3.11 -m venv .venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)"

deps:
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

lock:
	@if command -v pip-compile >/dev/null 2>&1; then \
		pip-compile requirements.in --output-file requirements.txt; \
		echo "Dependencies locked to requirements.txt"; \
	else \
		echo "pip-tools not installed. Run: pip install pip-tools"; \
		exit 1; \
	fi

db-init:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Copy .env.example to .env and configure."; \
		exit 1; \
	fi
	@echo "Initializing database schema..."
	@.venv/bin/python -c "from db.session import init_db; from common.env_readers import load_yaml_with_env; init_db(load_yaml_with_env('configs/db.yaml'))" || \
	mysql -h$$(grep MYSQL_HOST .env | cut -d '=' -f2) \
	      -P$$(grep MYSQL_PORT .env | cut -d '=' -f2) \
	      -u$$(grep MYSQL_USER .env | cut -d '=' -f2) \
	      -p$$(grep MYSQL_PASSWORD .env | cut -d '=' -f2) \
	      $$(grep MYSQL_DB .env | cut -d '=' -f2) < db/schema.sql
	@echo "Database initialized."

migrate:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Configure database credentials first."; \
		exit 1; \
	fi
	@echo "Running typing migrations..."
	@mysql --host=$$(grep MYSQL_HOST .env | cut -d '=' -f2) \
	       --port=$$(grep MYSQL_PORT .env | cut -d '=' -f2) \
	       -u$$(grep MYSQL_USER .env | cut -d '=' -f2) \
	       -p$$(grep MYSQL_PASSWORD .env | cut -d '=' -f2) \
	       $$(grep MYSQL_DB .env | cut -d '=' -f2) < db/migrations/2025_10_14_add_typing_columns.sql
	@echo "Typing migration complete."

migrate-agentic:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Configure database credentials first."; \
		exit 1; \
	fi
	@echo "Running agentic search migrations..."
	@mysql --host=$$(grep MYSQL_HOST .env | cut -d '=' -f2) \
	       --port=$$(grep MYSQL_PORT .env | cut -d '=' -f2) \
	       -u$$(grep MYSQL_USER .env | cut -d '=' -f2) \
	       -p$$(grep MYSQL_PASSWORD .env | cut -d '=' -f2) \
	       $$(grep MYSQL_DB .env | cut -d '=' -f2) < db/migrations/2025_10_14_agentic_plan_and_iter.sql
	@echo "Agentic migration complete."

migrate-chunks:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Configure database credentials first."; \
		exit 1; \
	fi
	@echo "Running chunk tables migrations..."
	@mysql --host=$$(grep MYSQL_HOST .env | cut -d '=' -f2) \
	       --port=$$(grep MYSQL_PORT .env | cut -d '=' -f2) \
	       -u$$(grep MYSQL_USER .env | cut -d '=' -f2) \
	       -p$$(grep MYSQL_PASSWORD .env | cut -d '=' -f2) \
	       $$(grep MYSQL_DB .env | cut -d '=' -f2) < db/migrations/2025_10_14_create_chunk_tables.sql
	@echo "Chunk tables migration complete."

search:
	.venv/bin/python pipelines/search_pipeline.py \
		--config configs/cse.yaml \
		--db configs/db.yaml \
		--query "RN 259 ANS" \
		--topn 100

ingest:
	.venv/bin/python pipelines/ingest_pipeline.py \
		--config configs/ingest.yaml \
		--db configs/db.yaml \
		--limit 100

agentic-example:
	@echo "Running agentic search with example plan (PDF/ZIP)..."
	.venv/bin/python scripts/run_agentic.py \
		--plan-file examples/agentic_plan_example.json \
		--debug

agentic-html:
	@echo "Running agentic search for HTML pages..."
	.venv/bin/python scripts/run_agentic.py \
		--plan-file examples/agentic_plan_html_only.json \
		--debug

agentic-view:
	@if [ -z "$(PLAN_ID)" ]; then \
		echo "Usage: make agentic-view PLAN_ID=<uuid>"; \
		exit 1; \
	fi
	.venv/bin/python scripts/view_agentic_iters.py $(PLAN_ID)

ui:
	@echo "========================================="
	@echo "  🌐 Agentic Search Console"
	@echo "========================================="
	@echo ""
	@echo "Starting API server..."
	@echo "Open in browser: http://localhost:8000/ui"
	@echo ""
	@echo "Press Ctrl+C to stop"
	@echo ""
	.venv/bin/uvicorn apps.api.main:app --reload --port 8000

api:
	.venv/bin/uvicorn apps.api.main:app --reload --port 8000

lint:
	.venv/bin/ruff check .
	.venv/bin/black --check .

test:
	.venv/bin/pytest tests/ -v

typecheck:
	.venv/bin/mypy --ignore-missing-imports --no-strict-optional agentic/ pipelines/ apps/ db/ common/ ingestion/ vector/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf data/downloads/* data/output/*

license-headers:
	@echo "Adding MIT license headers to source files..."
	@python tools/add_mit_headers.py
	@echo "✅ License headers applied!"

