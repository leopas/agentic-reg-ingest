# Estratégia de Cache para Vision Enrichment Pipeline

## 🎯 Objetivo
Evitar reprocessamento caro de OCR, Gemini e GPT para arquivos já processados.

## 📊 Níveis de Cache

### Nível 1: Upload (✅ JÁ IMPLEMENTADO)
- **Key:** SHA256 do arquivo
- **Value:** upload_id anterior
- **Storage:** MySQL (`vision_upload.file_hash`)
- **Lifetime:** Permanente
- **Comportamento:** Se upload duplicado, retorna upload_id existente

### Nível 2: OCR + Gemini (❌ FALTA IMPLEMENTAR)
- **Key:** `file_hash` + `ocr_version` + `gemini_version`
- **Value:** JSONL path
- **Storage:** MySQL (`vision_upload.jsonl_path`) + filesystem
- **Lifetime:** Permanente
- **Comportamento:** 
  - Se `jsonl_path` existe E arquivo existe → **SKIP OCR/Gemini**
  - Pula direto para estágio 3 (Allowlist)

### Nível 3: Allowlist (❌ FALTA IMPLEMENTAR)
- **Key:** SHA256 do JSONL content
- **Value:** AllowlistPlan JSON
- **Storage:** Filesystem (`data/cache/allowlist/{jsonl_hash}.json`)
- **Lifetime:** 7 dias (configurável)
- **Comportamento:**
  - Se cache existe e não expirou → **SKIP GPT call**
  - Usa plan cacheado

### Nível 4: Agentic Search (⚠️ PARCIALMENTE IMPLEMENTADO)
- **Key:** Plan hash (goal + queries + domains)
- **Value:** plan_id
- **Storage:** MySQL (`agentic_plan`)
- **Lifetime:** Configurável (TTL_DAYS)
- **Comportamento:** Já reutiliza plans similares via LLM

### Nível 5: Scraper (✅ JÁ IMPLEMENTADO)
- **Key:** doc_hash do conteúdo
- **Value:** .txt file
- **Storage:** Filesystem + header check
- **Lifetime:** Permanente
- **Comportamento:** Se doc_hash existe → SKIP download

## 🔄 Fluxo com Cache Otimizado

```
┌──────────────┐
│ Upload File  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Check file_hash      │ ← CACHE NÍVEL 1
│ Exists in DB?        │
└──────┬───────────────┘
       │ No → Continue
       │ Yes → Return existing upload_id
       ▼
┌──────────────────────┐
│ Save file + Create   │
│ upload record        │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Run Pipeline         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Check jsonl_path     │ ← CACHE NÍVEL 2
│ Exists?              │
└──────┬───────────────┘
       │ No → OCR + Gemini
       │ Yes → Load cached JSONL
       ▼
┌──────────────────────┐
│ Check allowlist      │ ← CACHE NÍVEL 3
│ cache?               │
└──────┬───────────────┘
       │ No → GPT call
       │ Yes → Load cached plan
       ▼
┌──────────────────────┐
│ Agentic Search       │ ← CACHE NÍVEL 4 (já existe)
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Scraper              │ ← CACHE NÍVEL 5 (já existe)
│ (check doc_hash)     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Vector Push          │
└──────────────────────┘
```

## 💰 Economia Estimada

### Sem Cache:
- Upload duplicado: 100% reprocessamento
- OCR: ~$0.001/página (Google Vision)
- Gemini: ~$0.01/página (multimodal)
- GPT: ~$0.001/plan
- Tempo: ~30s por documento

### Com Cache (Nível 2):
- Upload duplicado: 0% reprocessamento OCR/Gemini
- Economia: ~$0.011/página
- Tempo: ~3s (apenas Agentic + Scraper)

### Com Cache (Nível 3):
- Upload duplicado + JSONL similar: 0% GPT calls
- Economia adicional: ~$0.001/plan
- Tempo: ~2s (apenas Agentic + Scraper)

## 🚀 Implementação Prioritária

### P0 (Crítico) - Nível 2: OCR/Gemini Cache
**Impacto:** Alto (economiza 90% do tempo/custo)
**Esforço:** Baixo (5 linhas de código)

```python
# enrichment_pipeline.py linha ~95
if upload.jsonl_path and Path(upload.jsonl_path).exists():
    logger.info("enrichment_cache_hit_jsonl", path=upload.jsonl_path)
    # Skip to stage 3
    jsonl_path = Path(upload.jsonl_path)
else:
    # Run OCR + Gemini (código atual)
    ...
```

### P1 (Importante) - Nível 3: Allowlist Cache
**Impacto:** Médio (economiza GPT calls)
**Esforço:** Médio (20 linhas + cache manager)

```python
# Criar: agentic/enrichment/allowlist_cache.py
class AllowlistCache:
    def get(self, jsonl_hash: str) -> Optional[AllowlistPlan]:
        cache_file = Path(f"data/cache/allowlist/{jsonl_hash}.json")
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < TTL_SECONDS:
                return AllowlistPlan.parse_file(cache_file)
        return None
    
    def set(self, jsonl_hash: str, plan: AllowlistPlan):
        cache_file = Path(f"data/cache/allowlist/{jsonl_hash}.json")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(plan.json())
```

### P2 (Nice to have) - Cache Stats Dashboard
**Impacto:** Baixo (visibilidade)
**Esforço:** Alto (UI + métricas)

## ⚙️ Configuração

```yaml
# configs/vision_enrichment.yaml
cache:
  enabled: true
  
  ocr_gemini:
    enabled: true
    revalidate_after_days: 30  # Reprocessar após 30 dias
  
  allowlist:
    enabled: true
    ttl_days: 7
    max_size_mb: 100
  
  scraper:
    enabled: true  # Já implementado
```

## 🔍 Métricas a Monitorar

- `cache_hit_rate`: % de requests que usaram cache
- `time_saved_seconds`: Tempo economizado
- `cost_saved_usd`: Custo economizado (API calls)
- `cache_size_mb`: Tamanho total do cache

## 🧹 Limpeza de Cache

```python
# Estratégia LRU (Least Recently Used)
def cleanup_old_cache(max_age_days=30):
    """Remove cache files older than max_age_days."""
    for cache_file in Path("data/cache").rglob("*.json"):
        age_days = (time.time() - cache_file.stat().st_mtime) / 86400
        if age_days > max_age_days:
            cache_file.unlink()
```

## ✅ Checklist de Implementação

- [ ] Nível 2: OCR/Gemini cache
- [ ] Nível 3: Allowlist cache
- [ ] Cache config no YAML
- [ ] Cache stats logging
- [ ] Cleanup job (cronjob)
- [ ] Cache invalidation API
- [ ] Dashboard de métricas

