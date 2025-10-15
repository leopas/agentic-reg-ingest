<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 🚀 Referência Rápida - agentic-reg-ingest

## ⚡ Comandos Mais Usados

### Setup Inicial
```bash
python3.11 -m venv .venv                    # Criar venv
source .venv/bin/activate                   # Ativar (Linux/Mac)
.venv\Scripts\activate                      # Ativar (Windows)
pip install -r requirements.txt             # Instalar deps
cp .env.example .env                        # Criar .env
docker compose up -d mysql                  # Iniciar MySQL
make db-init                                # Criar tabelas
```

### Rodar Pipelines
```bash
make search                                 # Pipeline de busca
make ingest                                 # Pipeline de ingestão
make api                                    # Servidor FastAPI
```

### Debug no VSCode/Cursor
```
1. Ctrl+Shift+D (abrir debug)
2. Selecionar "Debug: Search Pipeline"
3. F5 (iniciar)
4. F10 (step over), F11 (step into)
```

### Testes e Qualidade
```bash
make test                                   # Rodar testes
make lint                                   # Linters
make typecheck                              # Type checking
```

---

## 📁 Estrutura do Projeto

```
agentic-reg-ingest/
├── apps/api/                 → FastAPI endpoints
│   ├── main.py              → Aplicação principal
│   └── middleware.py        → Logging middleware
│
├── agentic/                  → Core search & AI
│   ├── cse_client.py        → Google CSE
│   ├── scoring.py           → Score algorithm
│   ├── normalize.py         → URL normalization
│   └── llm.py               → OpenAI wrapper
│
├── pipelines/                → Pipeline orchestration
│   ├── search_pipeline.py   → 🔍 PIPELINE 1
│   ├── ingest_pipeline.py   → 📥 PIPELINE 2
│   ├── routers.py           → Document router
│   └── executors/           → Type-specific processors
│       ├── pdf_ingestor.py  → PDF processing
│       ├── zip_ingestor.py  → ZIP/tables
│       └── html_ingestor.py → HTML extraction
│
├── ingestion/                → Chunking & embedding prep
│   ├── anchors.py           → Anchor detection
│   ├── chunkers.py          → Token-aware chunking
│   └── emitters.py          → JSONL output
│
├── db/                       → Database layer
│   ├── schema.sql           → MySQL schema
│   ├── models.py            → SQLAlchemy models
│   ├── session.py           → Session management
│   └── dao.py               → Data access objects
│
├── common/                   → Shared utilities
│   ├── settings.py          → Pydantic settings
│   └── env_readers.py       → YAML + ${VAR} loader
│
├── configs/                  → Configuration files
│   ├── cse.yaml             → Search config
│   ├── db.yaml              → Database config
│   └── ingest.yaml          → Ingest config
│
├── vector/                   → Vector database
│   ├── qdrant_loader.py     → Load to Qdrant
│   └── settings.yaml        → Qdrant config
│
└── tests/                    → Test suite
    ├── test_scoring.py      → Scoring tests
    ├── test_router_llm.py   → Router tests
    └── test_pdf_markers.py  → Anchor tests
```

---

## 🔑 Variáveis de Ambiente (.env)

```env
# Obrigatórias
GOOGLE_API_KEY=xxx              # Google Cloud Console
GOOGLE_CX=xxx                   # Custom Search Engine ID
OPENAI_API_KEY=sk-xxx           # OpenAI API
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=xxx
MYSQL_DB=reg_cache

# Opcionais
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
REQUEST_TIMEOUT_SECONDS=30      # Timeout HTTP
TTL_DAYS=7                      # Cache TTL
QDRANT_URL=http://localhost:6333
```

---

## 🎯 Fluxo das Pipelines

### Pipeline 1: Search
```
Query → Google CSE → Normalize URLs → HEAD requests → Score → Rank → MySQL Cache
                                                                      ↓
                                                            Update document_catalog
```

### Pipeline 2: Ingest
```
DB (NEW/CHANGED) → Route (PDF/ZIP/HTML) → Download → Process → Chunk → JSONL
                           ↓
                    LLM sugere markers → Anchor detection → Smart chunking
```

---

## 🔍 Breakpoints Úteis

### search_pipeline.py
- **Linha ~87**: `def execute()` - Início da pipeline
- **Linha ~100**: Após verificar cache
- **Linha ~115**: Após chamar Google CSE
- **Linha ~130**: Loop de scoring

### ingest_pipeline.py
- **Linha ~70**: `def execute()` - Início
- **Linha ~85**: Loop de documentos
- **Linha ~95**: Routing decision
- **Linha ~105**: Chamada ao ingestor

### pdf_ingestor.py
- **Linha ~78**: `def ingest()` - Início
- **Linha ~85**: Download PDF
- **Linha ~90**: Extract text
- **Linha ~100**: LLM marker suggestion

---

## 📊 Consultas MySQL Úteis

```sql
-- Ver queries em cache
SELECT cache_key, query_text, result_count, created_at 
FROM search_query 
ORDER BY created_at DESC 
LIMIT 10;

-- Top 10 resultados por score
SELECT sr.url, sr.title, sr.score, sq.query_text
FROM search_result sr
JOIN search_query sq ON sr.query_id = sq.id
ORDER BY sr.score DESC
LIMIT 10;

-- Documentos prontos para ingestão
SELECT canonical_url, title, ingest_status, last_checked_at
FROM document_catalog
WHERE ingest_status = 'pending'
ORDER BY last_checked_at DESC;

-- Estatísticas
SELECT 
    ingest_status, 
    COUNT(*) as count 
FROM document_catalog 
GROUP BY ingest_status;
```

---

## 🐳 Docker Commands

```bash
# Iniciar serviços
docker compose up -d                    # Todos
docker compose up -d mysql              # Só MySQL
docker compose up -d qdrant             # Só Qdrant

# Status
docker compose ps

# Logs
docker compose logs -f api
docker compose logs -f mysql

# Parar
docker compose stop
docker compose down                     # Para e remove containers
docker compose down -v                  # Para e remove volumes (⚠️ apaga dados)

# Shell no container
docker compose exec mysql bash
docker compose exec mysql mysql -u root -p reg_cache
```

---

## 🌐 API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Search
curl -X POST http://localhost:8000/run/search \
  -H "Content-Type: application/json" \
  -d '{"query": "RN 259 ANS", "topn": 50}'

# Ingest
curl -X POST http://localhost:8000/run/ingest \
  -H "Content-Type: application/json" \
  -d '{"limit": 20}'

# Docs
open http://localhost:8000/docs          # Swagger UI
```

---

## 🧪 Testes

```bash
# Todos os testes
pytest tests/ -v

# Arquivo específico
pytest tests/test_scoring.py -v

# Teste específico
pytest tests/test_scoring.py::test_score_authority_gov_domain -v

# Com coverage
pytest tests/ --cov=. --cov-report=html

# Apenas testes rápidos (excluir slow)
pytest -m "not slow"
```

---

## 📦 Arquivos de Output

```
data/
├── downloads/              → PDFs/ZIPs baixados
│   ├── 12345.pdf
│   └── 67890.zip
│
└── output/                 → Knowledge base
    └── kb_regulatory.jsonl → Chunks prontos para embedding
```

---

## 🎨 Atalhos do VSCode/Cursor

| Atalho | Ação |
|--------|------|
| `F5` | Start debugging |
| `Ctrl+Shift+D` | Abrir debug panel |
| `F9` | Toggle breakpoint |
| `F10` | Step over |
| `F11` | Step into |
| `Shift+F11` | Step out |
| `Ctrl+Shift+F5` | Restart debug |
| `Ctrl+` ` | Toggle terminal |
| `Ctrl+Shift+P` | Command palette |

---

## 🔧 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Can't connect to DB | `docker compose restart mysql` |
| Invalid API key | Verificar `.env` |
| Import errors | Verificar interpretador Python (.venv) |
| Port 8000 in use | `lsof -ti:8000 \| xargs kill` (Mac/Linux) |

---

## 📚 Documentação Adicional

- `README.md` - Documentação completa
- `DEBUG_GUIDE.md` - Guia detalhado de debug
- `QUICKSTART_CHECKLIST.md` - Checklist de setup
- `CONTRIBUTING.md` - Como contribuir
- `CHANGELOG.md` - Histórico de mudanças

---

**💡 Dica**: Mantenha este arquivo aberto em uma aba para consulta rápida!

