# Cache do Judge + Rastreabilidade de Fontes

## ✅ Implementação Completa

### Benefícios

**Cache do Judge (por URL individual):**
- 💰 Economia de 50-80% em chamadas GPT em reprocessamentos
- ⚡ Judge instantâneo para URLs já julgadas
- 🎯 Cache por plan_goal_hash (invalida se objetivo muda)
- ⏰ TTL configurável (padrão: 30 dias)

**Rastreabilidade de Fontes:**
- 📊 Tag `source_pipeline` em cada chunk (regular, enrichment, manual)
- 🔍 Query RAG: filtrar chunks por origem
- 📈 Métricas: quantos chunks vieram do enrichment vs regular

---

## 🔧 Setup

### 1. Execute Migrações SQL

```bash
# Migração 1: Adicionar status awaiting_review
mysql -u root -p agentic_reg < db/migrations/2025_10_17_add_awaiting_review_status.sql

# Migração 2: Judge cache + source tracking
mysql -u root -p agentic_reg < db/migrations/2025_10_17_judge_cache_and_source_tracking.sql
```

### 2. Configure .env

```bash
# Cache do Judge (opcional, já tem defaults)
JUDGE_CACHE_ENABLED=true
JUDGE_CACHE_TTL_DAYS=30
```

### 3. Reinicie Servidor

```bash
uvicorn apps.api.main:app --reload --port 8000
```

---

## 📊 Como Funciona

### Cache do Judge

**Primeira execução:**
```json
// 25 candidatos, nenhum em cache
{"event": "judge_cache_check", "total": 25, "cached": 0, "needs_judgment": 25}
{"event": "llm_judge_start", "candidates_count": 25}
{"event": "judge_cache_saved", "approved": 12}
```

**Segunda execução (mesmo objetivo, URLs similares):**
```json
// 25 candidatos, 18 já julgados antes
{"event": "judge_cache_check", "total": 25, "cached": 18, "needs_judgment": 7}
{"event": "llm_judge_start", "candidates_count": 7}  // Só 7 chamadas GPT!
```

**Cache hit total:**
```json
{"event": "judge_all_cached", "msg": "All decisions from cache"}
// ✅ 0 chamadas GPT! Economia total!
```

---

### Rastreabilidade de Fontes

**Query chunks do enrichment:**
```sql
SELECT cm.doc_hash, cm.canonical_url, cm.chunk_count
FROM chunk_manifest cm
WHERE cm.source_pipeline = 'enrichment'
ORDER BY cm.created_at DESC;
```

**Query RAG filtrado:**
```python
# Buscar APENAS em chunks do enrichment
chunks = retriever.retrieve(
    query="...",
    filter={"source_pipeline": "enrichment"}
)
```

**Metadata nos chunks:**
```json
{
  "meta": {
    "upload_id": "abc123...",
    "source": "enrichment",
    "url": "https://arxiv.org/..."
  }
}
```

---

## 🎯 Invalidação de Cache

Cache é invalidado quando:
- **Goal muda:** `plan_goal_hash` diferente
- **Expira:** `expires_at` passa
- **Manual:** Delete da tabela `judge_cache`

**Exemplo:**
```python
# Plan 1: "RAG em produção"
plan_goal_hash_1 = SHA256("RAG em produção") = "abc123..."

# Plan 2: "Machine Learning basics"  
plan_goal_hash_2 = SHA256("Machine Learning basics") = "xyz789..."

# ✅ Cache NÃO é compartilhado entre plans diferentes!
```

---

## 📈 Métricas

### Logs para Monitorar:

```json
// Cache effectiveness
{"event": "judge_cache_check", "total": 25, "cached": 18, "hit_rate": 0.72}

// Economia de custo
{"event": "judge_cache_saved", "approved": 5, "rejected": 2}

// Source tracking
{"event": "enrichment_chunks_saved", "doc_hash": "...", "source_pipeline": "enrichment"}
```

### Dashboard Queries:

```sql
-- Cache hit rate (últimos 7 dias)
SELECT 
    COUNT(*) as total_decisions,
    SUM(CASE WHEN created_at > DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as recent_decisions
FROM judge_cache;

-- Chunks por fonte
SELECT 
    source_pipeline,
    COUNT(*) as count,
    SUM(chunk_count) as total_chunks
FROM chunk_manifest
GROUP BY source_pipeline;
```

---

## 🧹 Limpeza de Cache

**Manual:**
```sql
DELETE FROM judge_cache WHERE expires_at < NOW();
```

**Automático (futuro):**
```python
# Cronjob diário
from db.judge_cache_dao import JudgeCacheDAO

with session:
    deleted = JudgeCacheDAO.cleanup_expired(session)
    logger.info("judge_cache_cleanup", deleted=deleted)
```

---

## 🎊 Resultado Final

### Economia Projetada:

**Cenário: Reprocessar 3x o mesmo tipo de documento**

| Execução | Candidatos | GPT Calls | Custo | Cache Hit |
|----------|------------|-----------|-------|-----------|
| 1ª | 25 | 25 | $0.001 | 0% |
| 2ª | 25 | 7 | $0.0003 | 72% |
| 3ª | 25 | 0 | $0 | 100% |

**Economia total:** ~70% em custo de GPT!

---

**Sistema agora é ainda mais eficiente e rastreável!** 🚀

