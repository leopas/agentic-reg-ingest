# Visão + Enriquecimento - Vision Enrichment Pipeline

## Visão Geral

Nova funcionalidade de pipeline completo que realiza:

1. **Upload** de documentos (.pdf, .pptx, .zip)
2. **OCR** via Google Vision API
3. **Análise Multimodal** via Gemini (figuras, inferências guiadas)
4. **Geração de JSONL** estruturado por página
5. **Allowlist Planning** via GPT (domínios confiáveis + queries)
6. **Agentic Search** com CSE (busca iterativa com gates de qualidade)
7. **Scraping** das URLs aprovadas
8. **Normalização** para .txt com metadata header
9. **Chunking** e **Vector Push** para Qdrant

## Estrutura de Arquivos

### Novos Componentes Criados

```
agentic/
├── vision/
│   ├── __init__.py
│   ├── vision_client.py         # Google Vision OCR wrapper
│   └── gemini_client.py         # Gemini multimodal wrapper
└── enrichment/
    ├── __init__.py
    ├── gpt_allowlist_planner.py # GPT allowlist generator
    └── scraper.py               # Web scraper com normalização

ingestion/emitters/
└── txt_emitter.py               # Emissor TXT com metadata header

pipelines/
└── enrichment_pipeline.py       # Orquestrador principal

apps/api/
├── routes_vision_enrichment.py  # Rotas FastAPI
├── schemas/
│   └── vision_enrichment.py     # Pydantic models
└── templates/
    └── vision_enrichment.html   # UI HTMX

db/
├── models.py                    # + VisionUpload model
├── dao/
│   ├── __init__.py
│   └── upload_dao.py            # DAO para uploads
└── migrations/
    └── 2025_10_17_vision_upload_table.sql

configs/
└── vision_enrichment.yaml       # Configuração do pipeline
```

## Migração de Banco de Dados

Execute a migração SQL para criar a tabela `vision_upload`:

```bash
mysql -u <user> -p <database> < db/migrations/2025_10_17_vision_upload_table.sql
```

Ou via script Python:

```python
from db.session import DatabaseSession
from pathlib import Path

sql = Path("db/migrations/2025_10_17_vision_upload_table.sql").read_text()
db_session = DatabaseSession()
with next(db_session.get_session()) as session:
    session.execute(sql)
    session.commit()
```

## Configuração

### Variáveis de Ambiente (.env)

Certifique-se de que as seguintes variáveis estejam configuradas:

```bash
# Google APIs (Vision + Gemini)
GOOGLE_API_KEY=<sua_chave_google>

# OpenAI (para allowlist planning)
OPENAI_API_KEY=<sua_chave_openai>

# CSE (para Agentic Search)
GOOGLE_CX=<seu_cx_id>

# Qdrant (para vector push)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
RAG_COLLECTION=kb_regulatory

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=agentic_reg
MYSQL_USER=root
MYSQL_PASSWORD=

# Chunking
CHUNK_MAX_TOKENS=512
CHUNK_OVERLAP_TOKENS=50
```

### Arquivo de Configuração

Ajuste `configs/vision_enrichment.yaml` conforme necessário:

```yaml
llm:
  model: gpt-4o-mini
  temperature: 0
  max_tokens: 3000

scraper:
  timeout: 20

chunker:
  max_tokens: 512
  overlap_tokens: 50
  min_tokens: 100

upload:
  max_file_size_mb: 50
  allowed_extensions: [".pdf", ".pptx", ".ppt", ".zip"]
```

## Como Usar

### 1. Via UI (HTMX)

Acesse: **http://localhost:8000/ui/vision-enrichment**

**Fluxo:**
1. Faça upload do arquivo
2. Clique em "Rodar Pipeline"
3. Acompanhe o progresso em tempo real (cards de status)
4. Baixe o JSONL quando pronto
5. Clique em "Empurrar para VectorDB" ao final

### 2. Via API

#### Upload

```bash
curl -X POST http://localhost:8000/vision/upload \
  -F "files=@documento.pdf"
```

Resposta:
```json
{
  "upload_id": "abc123...",
  "status": "uploaded",
  "message": "File uploaded successfully"
}
```

#### Rodar Pipeline

```bash
curl -X POST http://localhost:8000/vision/run/{upload_id}
```

#### Verificar Status

```bash
curl http://localhost:8000/vision/status/{upload_id}
```

Resposta:
```json
{
  "upload_id": "abc123...",
  "status": "processing",
  "stage_ocr": "completed",
  "stage_multimodal": "running",
  "stage_allowlist": "pending",
  "stage_agentic": "pending",
  "stage_scrape": "pending",
  "stage_vector": "pending",
  "jsonl_path": "data/output/jsonl/abc123.jsonl",
  "plan_id": "xyz789...",
  ...
}
```

#### Download JSONL

```bash
curl http://localhost:8000/vision/download/jsonl/{upload_id} -o output.jsonl
```

#### Push para Vector

```bash
curl -X POST "http://localhost:8000/vision/vector/push/{upload_id}?collection=kb_regulatory&overwrite=false"
```

### 3. Via Python

```python
from pipelines.enrichment_pipeline import EnrichmentPipeline
from common.env_readers import load_yaml_with_env

config = load_yaml_with_env("configs/vision_enrichment.yaml")
pipeline = EnrichmentPipeline(config)

# Rodar pipeline completo
result = pipeline.run(upload_id="abc123...")

# Push para vector
result = pipeline.push_to_vector(upload_id="abc123...", collection="kb_regulatory")
```

## Formato de Saída

### JSONL (por página)

```json
{
  "doc_id": "upload_abc123",
  "page": 1,
  "text": "Texto extraído via OCR...",
  "figures": [
    {
      "caption": "Diagrama do processo",
      "labels": ["diagram", "flowchart"],
      "bbox": {"x": 100, "y": 200, "width": 400, "height": 300},
      "confidence": 0.88
    }
  ],
  "guided_inferences": [
    {
      "hypothesis": "Documento trata de regulamentação X",
      "rationale": "Baseado em...",
      "evidence_spans": [
        {"start": 0, "end": 50, "text": "..."}
      ],
      "confidence": 0.82,
      "section_hint": "Capítulo 1"
    }
  ],
  "meta": {"filename": "documento.pdf"}
}
```

### TXT (por URL scraped)

```
===META===
url: https://exemplo.gov.br/doc.html
fetched_at: 2025-10-17T14:30:00Z
domain: exemplo.gov.br
doc_hash: 1a2b3c4d5e6f...
===CONTENT===
Texto normalizado do documento...
```

## Fluxo do Pipeline

```
┌─────────────┐
│   Upload    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  OCR (Vision)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Gemini    │ (figuras + inferências)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  GPT        │ (allowlist + queries)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Agentic Search│ (CSE iterativo)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Scraper    │ (URLs aprovadas)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│TXT Normalize│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Chunking   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Vector Push  │ (Qdrant)
└─────────────┘
```

## Idempotência

- **Upload**: hash SHA256 do arquivo evita duplicatas
- **Scrape**: hash SHA256 do texto normalizado evita reprocessamento
- **Vector Push**: `doc_hash:chunk_id` como ID determinístico no Qdrant

## Segurança

- Validação de extensões de arquivo
- Validação de tamanho máximo (50MB padrão)
- Sanitização de nomes de arquivo
- Rate limiting nos wrappers de API (TODO: implementar)

## Observabilidade

- Logs estruturados via `structlog`
- Tracking de status por stage no banco de dados
- Polling automático de status na UI (3s)
- Trace IDs em erros (TODO: implementar)

## Testes

Execute testes básicos:

```bash
# Unit tests para componentes individuais
pytest tests/test_vision_client.py
pytest tests/test_gemini_client.py
pytest tests/test_gpt_allowlist.py
pytest tests/test_scraper.py

# E2E test
pytest tests/test_enrichment_pipeline.py
```

## Troubleshooting

### Erro: "Google Vision API key not configured"

Configure `GOOGLE_API_KEY` no `.env`.

### Erro: "Pipeline already running"

Aguarde o pipeline atual terminar ou verifique o status via `/vision/status/{upload_id}`.

### Erro: "JSONL not yet generated"

O pipeline ainda está executando. Verifique o status do `stage_multimodal`.

### Chunking falha

Verifique `CHUNK_MAX_TOKENS` e `CHUNK_OVERLAP_TOKENS` no `.env` ou `configs/vision_enrichment.yaml`.

### Vector push falha

1. Verifique se Qdrant está rodando: `curl http://localhost:6333/collections`
2. Confirme `QDRANT_URL` e `RAG_COLLECTION` no `.env`
3. Verifique logs do pipeline: `/vision/status/{upload_id}`

## Roadmap

- [ ] Suporte real para Google Vision API (atualmente placeholder)
- [ ] Suporte real para Gemini API (atualmente placeholder)
- [ ] Processamento de arquivos ZIP com múltiplos slides/imagens
- [ ] Rate limiting nos wrappers de API
- [ ] Cache de embeddings
- [ ] Retry automático com backoff exponencial
- [ ] Webhooks para notificação de conclusão
- [ ] Suporte a batch upload (múltiplos arquivos)
- [ ] UI: visualização de figuras detectadas
- [ ] UI: preview de inferências guiadas
- [ ] Métricas Prometheus/Grafana

## Licença

SPDX-License-Identifier: MIT
Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

