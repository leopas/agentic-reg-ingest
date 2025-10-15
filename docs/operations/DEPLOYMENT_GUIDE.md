<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Deployment Guide

Guia completo de deploy para produção.

## 🎯 Prerequisites

### Infrastructure
- **Python**: 3.12 (⚠️ NOT 3.13 - SQLAlchemy incompatibility)
- **MySQL**: 8.0+ (ou Azure Database for MySQL)
- **Qdrant**: Latest (Docker ou cloud)
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recomendado para embeddings)
- **Disk**: 10GB+ (depende do volume de chunks)

### External Services
- Google Custom Search Engine (API key + CX)
- OpenAI API (ou LM Studio/Ollama local)

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/agentic-reg-ingest
cd agentic-reg-ingest
```

### 2. Python Environment
```bash
# Use Python 3.12!
python3.12 -m venv .venv

# Activate
source .venv/bin/activate        # Linux/Mac
# ou
.venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Environment Variables

```bash
cp .env.example .env
```

**Edit `.env`:**
```bash
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=agentic_user
MYSQL_PASSWORD=strong_password_here
MYSQL_DB=agentic_reg_ingest

# Google CSE
CSE_API_KEY=your_google_api_key
CSE_CX=your_custom_search_engine_id

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_BASE_URL=  # Optional: for local LLM
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBED_DIM=1536

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Empty for local
RAG_COLLECTION=kb_regulatory

# Pipeline
TTL_DAYS=30
```

### 2. Database Setup

**Option A: Local MySQL**
```bash
# Install MySQL 8.0
# Create database
mysql -u root -p -e "CREATE DATABASE agentic_reg_ingest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "CREATE USER 'agentic_user'@'localhost' IDENTIFIED BY 'password';"
mysql -u root -p -e "GRANT ALL ON agentic_reg_ingest.* TO 'agentic_user'@'localhost';"
```

**Option B: Docker MySQL**
```bash
docker run -d \
  --name mysql-agentic \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=agentic_reg_ingest \
  -e MYSQL_USER=agentic_user \
  -e MYSQL_PASSWORD=password \
  -v mysql_data:/var/lib/mysql \
  mysql:8.0
```

### 3. Run Migrations

```bash
make db-init             # Base schema
make migrate             # Typing columns
make migrate-agentic     # Agentic tables
make migrate-chunks      # Chunk tables
```

### 4. Start Qdrant

**Option A: Docker**
```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

**Option B: Qdrant Cloud**
```bash
# Set in .env:
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_api_key
```

---

## 🚀 Running the Application

### Development Mode

```bash
# Start API with auto-reload
make api
# or
uvicorn apps.api.main:app --reload --port 8000
```

### Production Mode

```bash
# Use Gunicorn with uvicorn workers
gunicorn apps.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**Systemd Service:**
```ini
[Unit]
Description=Agentic Reg Ingest API
After=network.target

[Service]
Type=notify
User=agentic
WorkingDirectory=/opt/agentic-reg-ingest
Environment="PATH=/opt/agentic-reg-ingest/.venv/bin"
ExecStart=/opt/agentic-reg-ingest/.venv/bin/gunicorn apps.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🐳 Docker Compose (Optional)

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DB}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
  
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
  
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MYSQL_HOST=mysql
      - QDRANT_URL=http://qdrant:6333
    env_file:
      - .env
    depends_on:
      - mysql
      - qdrant
    command: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000

volumes:
  mysql_data:
  qdrant_storage:
```

---

## ✅ Verification

### Health Check
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "db_ok": true,
  "cse_ready": true,
  "openai_ready": true
}
```

### Test Search
```bash
curl -X POST http://localhost:8000/run/search \
  -H "Content-Type: application/json" \
  -d '{"query":"RN 259 ANS","topn":10}'
```

### Access UIs
```
http://localhost:8000/ui    - Agentic Console
http://localhost:8000/chat  - RAG Chat
http://localhost:8000/docs  - API Docs
```

---

## 📊 Monitoring

Ver: [Observability Guide](OBSERVABILITY.md)

**Metrics to track:**
- API latency (p50, p95, p99)
- Error rate
- CSE quota usage
- LLM token usage
- Vector push throughput
- DB connection pool

**Tools:**
- Logs: structured JSON (structlog)
- Metrics: Prometheus (opcional)
- Tracing: OpenTelemetry (opcional)

---

[← Architecture](../architecture/ARCHITECTURE.md) | [Operations Runbook →](OPERATIONS_RUNBOOK.md)

