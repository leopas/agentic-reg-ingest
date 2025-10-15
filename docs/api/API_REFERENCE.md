<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# API Reference

Referência completa dos endpoints REST.

## 📡 Base URL

```
http://localhost:8000
```

**Production:** Atualizar com URL real

---

## 🔍 Endpoints

### Health & Info

#### GET /health
Health check do sistema.

**Response:**
```json
{
  "status": "healthy",
  "db_ok": true,
  "cse_ready": true,
  "openai_ready": true
}
```

#### GET /
Root endpoint com links úteis.

**Response:**
```json
{
  "service": "agentic-reg-ingest",
  "version": "2.0.0",
  "ui": {
    "agentic_console": "http://localhost:8000/ui",
    "rag_chat": "http://localhost:8000/chat"
  },
  "endpoints": {...}
}
```

---

### Agentic Search

#### POST /agentic/plan
Gera plano de busca a partir de prompt em linguagem natural.

**Request:**
```json
{
  "prompt": "Buscar RNs ANS sobre prazos, últimos 2 anos"
}
```

**Response:**
```json
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan": {
    "goal": "...",
    "queries": [...],
    "quality_gates": {...},
    "stop": {...}
  }
}
```

#### POST /agentic/run
Executa plano agentivo.

**Request:**
```json
{
  "plan_id": "550e8400-...",
  "plan_override": null
}
```

**Response:**
```json
{
  "plan_id": "...",
  "iterations": 2,
  "approved_total": 12,
  "stopped_by": "min_approved",
  "promoted_urls": [...]
}
```

#### GET /agentic/iters/{plan_id}
Retorna audit trail de iterações.

**Response:**
```json
{
  "plan_id": "...",
  "iterations": [
    {
      "iter_num": 1,
      "executed_queries": [...],
      "approved_urls": [...],
      "rejected": [...],
      "new_queries": [...]
    }
  ]
}
```

#### GET /agentic/approved
Lista documentos aprovados.

**Query Params:**
- `plan_id` (optional) - Filtrar por plano
- `limit` (default: 100) - Máximo de resultados

**Response:**
```json
{
  "count": 42,
  "docs": [
    {
      "url": "...",
      "title": "...",
      "final_type": "pdf",
      "score": 2.4,
      "doc_hash": "abc...",
      "cache_status": "done",
      "vector_status": "present",
      "chunk_count": 15
    }
  ]
}
```

---

### Ingestion

#### POST /ingest/regenerate
Regenera chunks para documentos.

**Request:**
```json
{
  "urls": ["https://..."],
  "doc_hashes": ["abc123"],
  "overwrite": true,
  "push_after": false,
  "collection": "kb_regulatory"
}
```

**Response:**
```json
{
  "processed": 5,
  "errors": [],
  "items": [
    {
      "doc_hash": "abc...",
      "chunk_count": 15,
      "status": "done",
      "vector_status": "none"
    }
  ]
}
```

#### GET /chunks/status
Status de manifests.

**Query Params:**
- `urls` - CSV de URLs
- `doc_hashes` - CSV de hashes

**Response:**
```json
{
  "manifests": [
    {
      "doc_hash": "abc",
      "url": "...",
      "status": "done",
      "chunk_count": 15,
      "vector_status": "present",
      "last_pushed_at": "2025-10-14T20:00:00Z"
    }
  ]
}
```

---

### Vector Operations

#### POST /vector/push
Push chunks para VectorDB.

**Request:**
```json
{
  "doc_hashes": ["abc123", "def456"],
  "collection": "kb_regulatory",
  "overwrite": false,
  "batch_size": 64
}
```

**Response:**
```json
{
  "pushed": 128,
  "skipped": 0,
  "collection": "kb_regulatory"
}
```

#### POST /vector/delete
Remove chunks do VectorDB.

**Request:**
```json
{
  "doc_hashes": ["abc123"],
  "collection": "kb_regulatory"
}
```

**Response:**
```json
{
  "deleted": 64,
  "collection": "kb_regulatory"
}
```

---

### RAG Chat

#### POST /chat/ask
Pergunta via RAG.

**Request:**
```json
{
  "question": "Quais prazos de consulta?",
  "mode": "grounded",
  "top_k": 8,
  "score_threshold": 0.7,
  "collection": "kb_regulatory"
}
```

**Response:**
```json
{
  "answer": "De acordo com...\n\nFontes: ...",
  "used": [
    {
      "doc_hash": "abc",
      "chunk_id": "0",
      "score": 0.92,
      "title": "RN 259",
      "url": "https://..."
    }
  ],
  "log": [...]
}
```

---

## 📖 Interactive Docs

**Swagger UI:**
```
http://localhost:8000/docs
```

**ReDoc:**
```
http://localhost:8000/redoc
```

---

[← Back](../index.md) | [Operations Runbook →](../operations/OPERATIONS_RUNBOOK.md)

