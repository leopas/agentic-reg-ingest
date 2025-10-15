<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Data Model

Modelo de dados completo: MySQL + Qdrant.

## 📊 MySQL Schema

### search_query (Cache de Queries)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BIGINT PK | ID único |
| `cache_key` | VARCHAR(64) UNIQUE | SHA256(query+cx+allow_domains) |
| `cx` | VARCHAR(255) | Context ID do CSE |
| `query_text` | TEXT | Query original |
| `allow_domains` | TEXT | Pipe-separated domains |
| `top_n` | INT | Número de resultados |
| `created_at` | TIMESTAMP | Quando criado |
| `expires_at` | TIMESTAMP | TTL |
| `result_count` | INT | Quantos results |

**Relacionamento:** 1:N com `search_result`

### search_result (Resultados)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BIGINT PK | ID único |
| `query_id` | BIGINT FK | Ref a search_query |
| `url` | TEXT | URL do resultado |
| `title` | TEXT | Título |
| `snippet` | TEXT | Trecho de descrição |
| `rank_position` | INT | Posição no ranking |
| `score` | DECIMAL(5,4) | Score multi-fator (0-5) |
| **Typing fields:** | | |
| `http_content_type` | VARCHAR(128) | Header Content-Type |
| `http_content_disposition` | VARCHAR(255) | Header Content-Disposition |
| `url_ext` | VARCHAR(16) | Extensão da URL |
| `detected_mime` | VARCHAR(128) | MIME detectado |
| `detected_ext` | VARCHAR(16) | Extensão detectada |
| `final_type` | ENUM | pdf, zip, html, unknown |
| `fetch_status` | ENUM | ok, redirected, blocked, error |
| `last_modified` | TIMESTAMP | Do cabeçalho HTTP |
| `approved` | BOOLEAN | Se aprovado pelo judge |
| `created_at` | TIMESTAMP | Quando inserido |

### document_catalog (Canonical Docs)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BIGINT PK | ID único |
| `canonical_url` | VARCHAR(2048) UNIQUE | URL normalizada |
| `content_type` | VARCHAR(100) | MIME type |
| `final_type` | ENUM | pdf, zip, html, unknown |
| `last_modified` | TIMESTAMP | Last-Modified header |
| `etag` | VARCHAR(255) | ETag header |
| `content_hash` | VARCHAR(64) | SHA256 do conteúdo |
| `title` | TEXT | Título do documento |
| `domain` | VARCHAR(255) | Domínio extraído |
| `first_seen_at` | TIMESTAMP | Primeira vez visto |
| `last_checked_at` | TIMESTAMP | Última verificação |
| `last_ingested_at` | TIMESTAMP | Última ingestão |
| `ingest_status` | VARCHAR(50) | pending, done, error |
| `error_message` | TEXT | Erro (se houver) |

### chunk_manifest (Manifesto de Chunks)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BIGINT PK | ID único |
| `doc_hash` | VARCHAR(64) UNIQUE | SHA256(url+last_modified+type) |
| `canonical_url` | VARCHAR(2048) | URL fonte |
| `source_file` | VARCHAR(512) | Path local (se aplicável) |
| `doc_type` | VARCHAR(50) | pdf, html, zip |
| `chunk_count` | INT | Número de chunks |
| `status` | VARCHAR(50) | queued, processing, done, error |
| `error_message` | TEXT | Erro (se houver) |
| `meta` | TEXT | JSON com metadata |
| `created_at` | TIMESTAMP | Criação |
| `updated_at` | TIMESTAMP | Última atualização |
| **Vector tracking:** | | |
| `last_pushed_at` | TIMESTAMP | Último push ao Qdrant |
| `last_pushed_collection` | VARCHAR(128) | Nome da collection |
| `vector_status` | ENUM | none, present, partial, error |

### chunk_store (Chunks Individuais)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BIGINT PK | ID único |
| `doc_hash` | VARCHAR(64) FK | Ref a chunk_manifest |
| `chunk_id` | VARCHAR(128) | ID do chunk (índice) |
| `chunk_index` | INT | Índice sequencial |
| `text_content` | TEXT | Texto do chunk |
| `tokens` | INT | Contagem de tokens |
| `anchors` | TEXT | JSON array de anchors |
| `chunk_metadata` | TEXT | JSON metadata |
| `created_at` | TIMESTAMP | Criação |

**UNIQUE KEY:** (doc_hash, chunk_id)

### agentic_plan (Planos de Busca)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BIGINT PK | ID único |
| `plan_id` | CHAR(36) | UUID do plano |
| `goal` | TEXT | Objetivo do plano |
| `plan_json` | JSON | Plan completo |
| `created_at` | TIMESTAMP | Criação |

### agentic_iter (Iterações do Loop)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BIGINT PK | ID único |
| `plan_id` | CHAR(36) | UUID do plano |
| `iter_num` | INT | Número da iteração |
| `executed_queries` | JSON | Queries executadas |
| `approved_urls` | JSON | URLs aprovadas |
| `rejected_json` | JSON | Rejeitados com motivos |
| `new_queries` | JSON | Queries propostas |
| `summary` | TEXT | Resumo da iteração |
| `created_at` | TIMESTAMP | Criação |

**UNIQUE KEY:** (plan_id, iter_num)

---

## 🗄️ Qdrant Schema

### Collection: kb_regulatory

**Vector:**
- Dimension: 1536 (text-embedding-3-small)
- Distance: Cosine

**Point ID:** Unsigned integer (determinístico via SHA256)

**Payload:**
```json
{
  "doc_hash": "abc123...",
  "chunk_id": "0",
  "chunk_index": 0,
  "point_id_readable": "abc123...:0",
  "text": "Art. 2º - Os prazos...",
  "source_type": "pdf",
  "url": "https://www.gov.br/ans/.../rn-259.pdf",
  "title": "RN 259/2011",
  "text_len": 1024,
  "tokens": 256,
  "anchor_type": "artigo",
  "anchor_text": "Art. 2º",
  "page_hint": 3,
  "pushed_at": "2025-10-14T20:00:00Z",
  "collection": "kb_regulatory"
}
```

---

## 🔑 Identificadores Únicos

### doc_hash
```python
canonical_url = normalize_url(url)
hash_input = canonical_url + last_modified + final_type
doc_hash = sha256(hash_input).hexdigest()
```

**Uso:**
- Chave primária em `chunk_manifest`
- Foreign key em `chunk_store`
- Payload em Qdrant points

### point_id (Qdrant)
```python
id_string = f"{doc_hash}:{chunk_index}"
id_hash = sha256(id_string).hexdigest()
point_id = int(id_hash[:16], 16)  # Unsigned integer
```

**Características:**
- Determinístico (mesmo input = mesmo ID)
- Idempotente (re-push atualiza, não duplica)
- Collision-safe (SHA256 de 64 bits)

---

## 🔄 Relacionamentos

```
search_query 1─────N search_result
                        │
                        └─ (url) ──> document_catalog
                                           │
                                           └─ (canonical_url) ─> chunk_manifest 1──N chunk_store
                                                                       │
                                                                       └─ (doc_hash) ─> Qdrant points
```

---

## 📈 Data Lifecycle

### Search Results
```
1. CSE query → search_query (cache_key, expires_at)
2. Results → search_result (approved=1 se passar gates)
3. Expires_at → auto-cleanup (pode implementar)
```

### Documents
```
1. Approved → document_catalog (canonical_url, final_type)
2. Diff check (ETag, Last-Modified, content_hash)
3. If NEW/CHANGED → trigger ingest
```

### Chunks
```
1. Ingest → chunk_manifest (doc_hash, status=processing)
2. Chunking → chunk_store (bulk insert)
3. Manifest update (status=done, chunk_count)
```

### Vector
```
1. Push → Qdrant points (deterministic IDs)
2. Manifest update (vector_status=present, last_pushed_at)
3. Re-push (overwrite) → delete old + insert new
```

---

[← Architecture](ARCHITECTURE.md) | [Next: Pipelines →](PIPELINES.md)

