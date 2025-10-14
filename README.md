# agentic-reg-ingest

Production-grade pipeline for searching and ingesting regulatory documents with intelligent chunking and vector storage.

## 🎯 Features

### Pipeline 1: Search & Cache
- Google Programmable Search Engine (CSE) integration
- Multi-factor scoring (authority, freshness, specificity, type, anchorability)
- MySQL caching with TTL
- Automatic URL normalization and metadata extraction

### Pipeline 2: Intelligent Ingestion
- Diff detection (NEW/CHANGED/SAME)
- LLM-powered intent routing (PDF/ZIP/HTML)
- PDF processing with LLM-suggested anchoring markers
- **HTML with LLM structure extraction** (sections, tables, anchors)
- PDF wrapper detection and re-routing
- Token-aware chunking with anchor alignment
- JSONL output for knowledge base
- Vector database (Qdrant) integration

## 🏗️ Architecture

```
agentic-reg-ingest/
├── apps/api/              # FastAPI REST endpoints
├── agentic/               # Core search & LLM clients
├── pipelines/             # Search & Ingest pipelines
│   └── executors/         # Type-specific ingestors
├── ingestion/             # Chunking, anchoring, emitting
├── db/                    # SQLAlchemy models & DAOs
├── common/                # Settings & config readers
├── configs/               # YAML configurations
├── vector/                # Qdrant loader
├── scripts/               # Helper scripts
└── tests/                 # Test suite
```

## 🎭 Typing & Routing

### Robust Document Type Detection

The pipeline uses a multi-layered detection strategy to accurately identify document types (PDF, ZIP, HTML) and prevent misrouting:

**Detection Priority (first match wins):**

1. **Magic Bytes** (highest priority) - Sniffs first 8 bytes via Range GET
   - `%PDF-` → PDF
   - `PK\x03\x04`, `PK\x05\x06`, `PK\x07\x08` → ZIP

2. **Content-Disposition** - Extracts filename from header
   - `filename="document.pdf"` → PDF

3. **Content-Type** - MIME type with URL extension disambiguation
   - `application/pdf` → PDF
   - `text/html` but URL ends in `.pdf` → PDF (trust extension)

4. **URL Extension** - Fallback to file extension
   - `.pdf`, `.zip`, `.html`

5. **Fallback** - Unknown (triggers LLM routing)

### Routing Strategy

**At Search Time** (`search_pipeline.py`):
- Detects type using all available signals
- Persists `final_type` to `search_result` and `document_catalog`
- Stores typing metadata: `http_content_type`, `detected_mime`, `url_ext`, `fetch_status`

**At Ingest Time** (`ingest_pipeline.py` → `routers.py`):
1. **Trust DB first** - If `final_type ∈ {pdf, zip, html}`, use it immediately
2. **Re-detect if unknown** - HEAD request + magic sniff
3. **LLM fallback** - Only if still unknown

**Executor Validation**:
- Each executor validates expected type before processing
- Fails fast if mismatch (e.g., PDF executor receives HTML)

### New Database Columns

**`search_result` table:**
```sql
http_content_type        VARCHAR(128)   -- Raw Content-Type header
http_content_disposition VARCHAR(255)   -- Content-Disposition header
url_ext                  VARCHAR(16)    -- URL extension (pdf, zip, html)
detected_mime            VARCHAR(128)   -- Detected MIME type
detected_ext             VARCHAR(16)    -- Detected extension
final_type               ENUM(...)      -- Final resolved type
fetch_status             ENUM(...)      -- ok, redirected, blocked, error
```

**`document_catalog` table:**
```sql
final_type               ENUM(...)      -- Cached type for routing
```

### Running Migrations

After pulling this update, run:

```bash
make migrate
```

Or manually:

```bash
mysql --host=$MYSQL_HOST --port=$MYSQL_PORT -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DB < db/migrations/2025_10_14_add_typing_columns.sql
```

## 🤖 Agentic Search (Plan→Act→Observe→Judge→Re-plan)

### Overview

**True agentic search** with autonomous loop that refines queries, applies quality gates, and only promotes high-quality, citable sources to the vector DB.

```
┌─────────────┐
│   PLAN      │ ← LLM generates search strategy
└──────┬──────┘
       ↓
┌─────────────┐
│    ACT      │ ← Execute queries via Google CSE
└──────┬──────┘
       ↓
┌─────────────┐
│  OBSERVE    │ ← Fetch metadata, detect types, score
└──────┬──────┘
       ↓
┌─────────────┐
│   JUDGE     │ ← Quality gates + LLM evaluation
└──────┬──────┘
       ↓
   ┌───────────┐     Stop?      ┌──────────┐
   │ Approved? │────────Yes─────→│   DONE   │
   └─────┬─────┘                 └──────────┘
         No
         ↓
   ┌───────────┐
   │  RE-PLAN  │ ← Merge new queries, iterate
   └─────┬─────┘
         │
         └───────→ (back to ACT)
```

### Key Features

**1. LLM Planner**
- Generates structured search plan from natural language prompt
- Outputs JSON with: goals, queries, quality gates, stop conditions
- Example prompt: *"Buscar todas as RNs da ANS sobre prazos de atendimento dos últimos 2 anos"*

**2. Agentic Loop**
- Executes 2-3 queries per iteration
- Fetches metadata and detects document types
- Applies **hard quality gates** (code-level)
- Asks LLM to **judge** candidates semantically
- Proposes **new queries** if gaps detected

**3. Quality Gates** (configurable)
```yaml
must_types: ["pdf", "zip"]      # Only official documents
max_age_years: 3                # Recent content only
min_anchor_signals: 1           # Must have Art./Anexo/Tabela
min_score: 0.65                 # Relevance threshold
```

**4. Stop Conditions**
- ✅ `min_approved` reached (e.g., 12 documents)
- ✅ `max_iterations` limit (e.g., 3)
- ✅ `budget` exceeded (max CSE calls)
- ✅ No progress (no approvals, no new queries)

**5. Full Audit Trail**
- Every iteration persisted to `agentic_plan` and `agentic_iter` tables
- Tracks: executed queries, approved URLs, rejected (with reasons), new queries
- Regulatory-compliant audit logs

### API Usage

#### Step 1: Create Plan

```bash
POST /agentic/plan
Content-Type: application/json

{
  "prompt": "Buscar RNs da ANS sobre cobertura obrigatória e prazos máximos de atendimento, publicadas nos últimos 2 anos"
}

Response:
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan": {
    "goal": "RNs ANS sobre cobertura e prazos (2023-2025)",
    "topics": ["cobertura obrigatória", "prazos atendimento"],
    "queries": [
      {"q": "RN ANS cobertura obrigatória", "why": "Base coverage rules", "k": 10},
      {"q": "RN ANS prazos máximos atendimento", "why": "Service timeline regulations", "k": 10}
    ],
    "allow_domains": ["www.gov.br/ans", "www.planalto.gov.br"],
    "deny_patterns": [".*blog.*", ".*noticia.*"],
    "stop": {"min_approved": 12, "max_iterations": 3, "max_queries_per_iter": 2},
    "quality_gates": {
      "must_types": ["pdf", "zip"],
      "max_age_years": 2,
      "min_anchor_signals": 1,
      "min_score": 0.7
    },
    "budget": {"max_cse_calls": 60, "ttl_days": 7}
  }
}
```

#### Step 2: (Optional) Edit Plan JSON

You can edit the returned plan JSON before execution:
- Add/remove queries
- Adjust quality gates
- Change stop conditions

#### Step 3: Execute Loop

```bash
POST /agentic/run
Content-Type: application/json

{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000"
}

# OR with custom plan:
{
  "plan_override": { ...edited_plan... }
}

Response:
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "iterations": 2,
  "approved_total": 15,
  "stopped_by": "min_approved",
  "promoted_urls": [
    "https://www.gov.br/ans/.../rn-395.pdf",
    "https://www.gov.br/ans/.../rn-428.pdf",
    ...
  ]
}
```

#### Step 4: Review Audit Trail

```bash
GET /agentic/iters/550e8400-e29b-41d4-a716-446655440000

Response:
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_iterations": 2,
  "iterations": [
    {
      "iter_num": 1,
      "executed_queries": ["RN ANS cobertura obrigatória", "RN ANS prazos máximos"],
      "approved_urls": ["https://.../rn-395.pdf", ...],
      "rejected": [
        {"url": "https://.../noticia-xyz", "reason": "Tipo não permitido", "violations": ["type:not_allowed"]}
      ],
      "new_queries": ["RN 259 ANS anexos"],
      "summary": "Iter 1: 8 approved, 12 rejected",
      "created_at": "2025-10-14T18:00:00"
    },
    {
      "iter_num": 2,
      "executed_queries": ["RN 259 ANS anexos"],
      "approved_urls": [...],
      "rejected": [...],
      "new_queries": [],
      "summary": "Iter 2: 7 approved, 3 rejected",
      "created_at": "2025-10-14T18:02:15"
    }
  ]
}
```

### Cost Control & Safety

**Budget Controls:**
- `max_cse_calls`: Hard limit on Google CSE API calls
- `ttl_days`: Cache TTL to avoid redundant searches
- `max_iterations`: Cap on loop iterations

**Safety Guardrails:**
- `allow_domains`: Whitelist official domains only
- `deny_patterns`: Blacklist blogs, news, forums
- Hard quality gates before LLM judge
- Deterministic LLM (temperature=0)

### Configuration

Default settings in `configs/agentic.yaml`:

```yaml
agentic:
  default_stop:
    min_approved: 12
    max_iterations: 3
    max_queries_per_iter: 2
  
  default_quality:
    must_types: ["pdf", "zip"]
    max_age_years: 3
    min_anchor_signals: 1
    min_score: 0.65
  
  budget:
    max_cse_calls: 60
    ttl_days: 7
```

### Why This is "True Agentic"

✅ **Autonomous Planning** - LLM generates search strategy  
✅ **Iterative Refinement** - Loops until goal achieved  
✅ **Self-Correction** - Judge rejects poor sources, proposes new queries  
✅ **Memory & State** - Tracks progress across iterations  
✅ **Goal-Oriented** - Stops when target reached or no progress  
✅ **Full Audit** - Every decision logged for compliance  

### Database Schema

Run migration:
```bash
make migrate-agentic
```

Creates tables:
- `agentic_plan` - Stores search plans (goals, queries, gates)
- `agentic_iter` - Audit trail of every iteration

### 🌐 Web UI (HTMX Console)

**Visual interface para operar o sistema via browser** - zero build, apenas HTML + HTMX!

```bash
# 1. Iniciar servidor
make ui

# 2. Abrir browser
http://localhost:8000/ui
```

**Features:**
- 🧠 **Gerar Plano** - Digite objetivo em linguagem natural, LLM gera plano
- ✏️ **Editar Plano** - Ajuste JSON antes de executar (queries, gates, domains)
- 🚀 **Executar Loop** - Roda Plan→Act→Observe→Judge→Re-plan com auto-refresh
- 📊 **Audit Trail** - Visualiza iterações em tempo real (refresh 3s)
- ✅ **Aprovados** - Lista documentos aprovados com links clicáveis
- 💾 **Download** - Exporta lista de aprovados como JSON
- ⚡ **Pipeline Shortcuts** - Botões rápidos para search/ingest

**Requisitos:** Nenhum! HTMX via CDN, HTML estático.

**Screenshots da UI:**

```
┌─────────────────────────────────────────────────┐
│ 🤖 Agentic Search Console                      │
│ Plan → Act → Observe → Judge → Re-plan | v2.0  │
├─────────────────────┬───────────────────────────┤
│ 1️⃣ Gerar Plano      │ 3️⃣ Iterações & Audit      │
│ [Textarea: prompt]  │ ┌─ ITERATION 1           │
│ [Gerar] [Exemplo]   │ │ ✅ 8 ✗ 5               │
│                     │ │ Queries: RN ANS...     │
│ Plan JSON editável  │ └─────────────────       │
│ [JSON textarea]     │                          │
├─────────────────────┤ ✅ Documentos Aprovados   │
│ 2️⃣ Executar Loop    │ • doc1.pdf              │
│ [plan_id input]     │ • doc2.pdf              │
│ [Executar]          │ [💾 Baixar Lista]       │
└─────────────────────┴───────────────────────────┘
```

### CLI Usage (Recommended for Development)

**Quick Start:**
```bash
# 1. Run with example plan
make agentic-example

# 2. Or create from prompt
python scripts/run_agentic.py --prompt "Buscar RNs da ANS sobre prazos de atendimento" --debug

# 3. View results
make agentic-view PLAN_ID=<uuid>
```

**Advanced Usage:**
```bash
# Generate plan only (for editing)
python scripts/run_agentic.py \
  --prompt "Buscar RNs ANS cobertura" \
  --plan-only \
  --output my_plan.json

# Edit my_plan.json manually, then:
python scripts/run_agentic.py --plan-file my_plan.json --debug

# Dry-run (simulate without DB)
python scripts/run_agentic.py --plan-file my_plan.json --dry-run
```

**See full guide:** [AGENTIC_QUICKSTART.md](AGENTIC_QUICKSTART.md)

## 📄 HTML Ingestion (LLM-Structured)

### Overview

HTML documents are processed through a sophisticated pipeline that uses **LLM to structure content** (not summarize) before chunking:

```
Download → Readability → PDF Wrapper Check → LLM Structure → Anchor-Aware Chunking → JSONL
```

### Key Features

**1. PDF Wrapper Detection**
- Detects HTML pages that are just wrappers for PDF files
- Checks: `<iframe>`, `<embed>`, `<meta refresh>`, download links
- Auto-routes to PDF ingestor when detected

**2. LLM Structure Extraction**
- **Does NOT summarize** - preserves all content in original order
- Extracts canonical JSON schema:
  ```json
  {
    "title": "Document Title",
    "language": "pt",
    "sections": [{"heading": "...", "text": "..."}],
    "tables": [{"caption": "...", "rows": 10}],
    "pdf_links": ["https://..."],
    "anchors": [{"type": "h1|h2|h3|h4|table", "value": "..."}]
  }
  ```
- Uses `gpt-4o-mini` with strict JSON mode
- Temperature = 0 for consistency

**3. Readability + trafilatura**
- Removes boilerplate (nav, ads, scripts)
- Extracts clean article text
- Collects headings and table markers
- Caps content to ~80k chars for LLM

**4. Anchor-Aware Chunking**
- Aligns chunk boundaries with headings/tables
- Respects min/max token limits
- Preserves semantic coherence

### Configuration

Enable/disable in `configs/ingest.yaml`:

```yaml
llm_html_extractor:
  enabled: true              # Set false for readability-only (no LLM cost)
  model: gpt-4o-mini
  max_chars: 120000          # Max chars to extract from HTML
  max_chars_llm: 80000       # Max chars sent to LLM
  temperature: 0
```

### Fallback Behavior

If `enabled: false`:
- Uses trafilatura/BeautifulSoup only
- No LLM calls (zero cost)
- Still collects basic anchors from headings
- Produces chunks without LLM-structured metadata

### Output Metadata

Each chunk includes:

```json
{
  "text": "...",
  "tokens": 450,
  "source_url": "https://...",
  "metadata": {
    "content_type": "text/html",
    "extracted_by": "llm+readability",
    "llm_model": "gpt-4o-mini",
    "language": "pt",
    "sections_count": 5,
    "anchors_count": 12,
    "anchors": [...]
  }
}
```

### PDF Wrapper Handling

When HTML ingestor detects a PDF wrapper:

1. Logs detection: `pdf_wrapper_detected`
2. Returns routing instruction: `{"next_type": "pdf", "next_url": "..."}`
3. Pipeline marks HTML as failed with note
4. PDF URL is logged for manual/automated re-processing

**Future enhancement:** Auto-enqueue detected PDF for ingestion.

## 📋 Requirements

- Python 3.11+
- MySQL 8.0+ (or Azure Database for MySQL)
- Google Custom Search API credentials
- OpenAI API key
- Qdrant (optional, for vector storage)
- **New:** trafilatura, BeautifulSoup4, lxml (for HTML extraction)

## 🚀 Quickstart

### Quick Links
- 📘 **[Agentic Search Quickstart](AGENTIC_QUICKSTART.md)** - Guia completo de uso
- 📄 **[Example Plan](examples/agentic_plan_example.json)** - Plano pronto para usar

## 🚀 Setup Básico

### 1. Clone and Setup

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required variables:
- `GOOGLE_API_KEY` - Google API key
- `GOOGLE_CX` - Custom Search Engine ID
- `OPENAI_API_KEY` - OpenAI API key
- `MYSQL_*` - Database credentials

### 3. Start Services (Docker)

```bash
# Start MySQL and Qdrant
docker compose up -d mysql qdrant

# Initialize database schema
make db-init
```

Alternatively, apply schema manually:
```bash
mysql -h localhost -u root -p reg_cache < db/schema.sql
```

### 4. Run Pipelines

#### Search Pipeline
```bash
# Using Makefile
make search

# Or directly
python pipelines/search_pipeline.py \
    --config configs/cse.yaml \
    --db configs/db.yaml \
    --query "RN 259 ANS" \
    --topn 100
```

#### Ingest Pipeline
```bash
# Using Makefile
make ingest

# Or directly
python pipelines/ingest_pipeline.py \
    --config configs/ingest.yaml \
    --db configs/db.yaml \
    --limit 100
```

### 5. Start API Server

```bash
# Using Makefile
make api

# Or directly
uvicorn apps.api.main:app --reload --port 8000
```

Access API at: http://localhost:8000

## 🔧 Development

### Run Tests
```bash
make test
# or
pytest tests/ -v
```

### Linting
```bash
make lint
# or
ruff check .
black --check .
```

### Type Checking
```bash
make typecheck
# or
mypy --ignore-missing-imports agentic/ pipelines/ apps/
```

### Dependency Management

Using `pip-tools` (optional):
```bash
# Install pip-tools
pip install pip-tools

# Update requirements.txt from requirements.in
make lock
# or
pip-compile requirements.in
```

## 📡 API Endpoints

### Health Check
```bash
GET /health

Response:
{
  "status": "ok",
  "db_ok": true,
  "cse_ready": true,
  "openai_ready": true
}
```

### Run Search Pipeline
```bash
POST /run/search
Content-Type: application/json

{
  "query": "RN 259 ANS",
  "topn": 100
}

Response:
{
  "results_count": 47,
  "message": "Search completed: 47 results found"
}
```

### Run Ingest Pipeline
```bash
POST /run/ingest
Content-Type: application/json

{
  "limit": 50
}

Response:
{
  "total": 50,
  "new": 30,
  "changed": 20,
  "success": 45,
  "failed": 5
}
```

## 🗂️ Configuration Files

### configs/cse.yaml
Google CSE settings, domain boosting, keyword patterns

### configs/db.yaml
MySQL connection, pool settings, TTL

### configs/ingest.yaml
LLM settings, chunking parameters, download config

### vector/settings.yaml
Qdrant connection, collection settings, embedding model

All configs support `${VAR}` placeholders resolved from `.env`

## 📊 Database Schema

### search_query
Cached search queries with TTL

### search_result
Individual search results with scoring

### document_catalog
Canonical document registry for diff detection

## 🎨 Vector Database (Optional)

Load chunks into Qdrant:

```bash
python vector/qdrant_loader.py \
    --config vector/settings.yaml \
    --input data/output/kb_regulatory.jsonl
```

Note: Update `vector/qdrant_loader.py` to use actual embedding model (e.g., sentence-transformers)

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker compose build

# Start all services
docker compose up -d

# View logs
docker compose logs -f api
```

### Production
For production, configure:
- Volume mounts for `data/`
- Environment variables via `.env`
- SSL/TLS for MySQL
- Reverse proxy (nginx) for API

## 🧪 Testing

Test suite includes:
- `test_scoring.py` - Scoring algorithm tests
- `test_router_llm.py` - Document routing tests
- `test_pdf_markers.py` - Anchor detection tests

Run with coverage:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

## 📝 Logging

All logs are JSON-formatted (structlog) with:
- ISO timestamps
- Trace IDs for request tracking
- No sensitive data (credentials masked)

Example log:
```json
{
  "event": "request_complete",
  "method": "POST",
  "path": "/run/search",
  "status_code": 200,
  "duration_ms": 1234.56,
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-10-14T10:30:00.123456Z"
}
```

## 🔒 Security

- **Never commit secrets** - Use `.env` (gitignored)
- **Fail fast** - App exits if required env vars missing
- **SQL injection protection** - SQLAlchemy ORM
- **Request validation** - Pydantic models
- **Rate limiting** - Consider adding to production API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linters: `make lint`
5. Run tests: `make test`
6. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Troubleshooting

### Database Connection Failed
- Check MySQL is running: `docker compose ps`
- Verify `.env` credentials
- Test connection: `mysql -h localhost -u user -p`

### Search Pipeline Fails
- Verify Google API key and CX in `.env`
- Check CSE quotas in Google Cloud Console
- Review logs for detailed errors

### Ingest Pipeline Hangs
- Check OpenAI API key
- Verify network connectivity
- Reduce `--limit` for testing

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📚 References

- [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/overview)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Vector Database](https://qdrant.tech/)

---

**Built with ❤️ for regulatory compliance and knowledge management**

