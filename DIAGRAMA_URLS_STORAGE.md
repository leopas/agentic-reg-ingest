# 📊 Diagrama: Armazenamento de URLs Aprovadas

## Fluxo Visual

```
┌──────────────────────────────────────────────────────────────┐
│  1. Upload PDF                                               │
│     upload_id: "07da1342..."                                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  2. OCR + Gemini → JSONL                                     │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  3. GPT Allowlist → Plan                                     │
│     plan_id: "af46e9f2..."                                   │
│     allow_domains: ["ans.gov.br", "anvisa.gov.br"]          │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Agentic Search (Iteração 1)                              │
│                                                              │
│  Google CSE Search:                                          │
│    - Query 1 → 10 URLs                                       │
│    - Query 2 → 10 URLs                                       │
│                                                              │
│  Judge LLM aprova:                                           │
│    ✓ https://ans.gov.br/legislacao/rn-123                   │
│    ✓ https://anvisa.gov.br/norma-456                        │
│    ✓ https://saude.gov.br/portaria-789                      │
│    ...                                                       │
│                                                              │
│  SALVA EM:                                                   │
│  ┌────────────────────────────────────────────────┐         │
│  │ agentic_iter                                   │         │
│  ├────────────────────────────────────────────────┤         │
│  │ id: 1                                          │         │
│  │ plan_id: "af46e9f2..."                         │         │
│  │ iteration_number: 1                            │         │
│  │ approved_urls: [                               │         │
│  │   "https://ans.gov.br/legislacao/rn-123",     │         │
│  │   "https://anvisa.gov.br/norma-456",          │         │
│  │   ...                                          │         │
│  │ ]                                              │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  E TAMBÉM EM (para cada URL):                                │
│  ┌────────────────────────────────────────────────┐         │
│  │ search_result                                  │         │
│  ├────────────────────────────────────────────────┤         │
│  │ id: 101                                        │         │
│  │ query_id: 50                                   │         │
│  │ url: "https://ans.gov.br/legislacao/rn-123"   │         │
│  │ title: "Resolução Normativa 123..."           │         │
│  │ snippet: "Esta RN trata de..."                │         │
│  │ score: 0.87                                    │         │
│  │ approved: TRUE                                 │         │
│  │ final_type: "pdf"                              │         │
│  └────────────────────────────────────────────────┘         │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Vision Upload Vinculado                                  │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │ vision_upload                                  │         │
│  ├────────────────────────────────────────────────┤         │
│  │ upload_id: "07da1342..."                       │         │
│  │ plan_id: "af46e9f2..."          ← LIGA TUDO!  │         │
│  │ status: "awaiting_review"                      │         │
│  └────────────────────────────────────────────────┘         │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Usuário Revisa URLs (UI)                                 │
│                                                              │
│  GET /vision/approved-urls/{upload_id}                       │
│  ↓                                                           │
│  1. Busca vision_upload por upload_id                        │
│  2. Pega plan_id do upload                                   │
│  3. Busca agentic_iter WHERE plan_id = ...                   │
│  4. Extrai approved_urls do JSON                             │
│  5. Busca search_result WHERE url IN (approved_urls)         │
│  6. Retorna lista com título, snippet, score                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  7. Scraping das URLs Selecionadas                           │
│                                                              │
│  POST /vision/scrape/{upload_id}                             │
│  Body: {selected_urls: ["url1", "url2"]}                     │
│                                                              │
│  Para cada URL:                                              │
│    - Faz scraping                                            │
│    - Salva .txt em data/output/enrichment_txt/               │
│    - Atualiza chunk_manifest                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Relacionamentos de Tabelas

```
vision_upload
    ↓ (plan_id)
agentic_plan
    ↓ (plan_id)
agentic_iter ──────────┐
    │                  │
    │ approved_urls    │ (JSON array)
    │ (JSON)           │
    │                  │
    ↓                  ↓
search_result    (usa as URLs do JSON para buscar detalhes)
    │
    │ url, title, snippet, score
    │
    ↓
chunk_manifest (depois do scraping)
    │
    │ doc_hash, canonical_url
    │
    ↓
Qdrant (vector database)
```

---

## 🔍 Como Recuperar URLs

### **Método 1: Via agentic_iter (JSON)**

```sql
SELECT approved_urls 
FROM agentic_iter 
WHERE plan_id = 'af46e9f2...'

-- Retorna: ["url1", "url2", "url3"]
```

### **Método 2: Via search_result (Detalhes Completos)**

```sql
SELECT url, title, snippet, score 
FROM search_result 
WHERE approved = TRUE 
  AND url IN (
    -- URLs do agentic_iter
    SELECT JSON_UNQUOTE(JSON_EXTRACT(approved_urls, '$[*]'))
    FROM agentic_iter 
    WHERE plan_id = 'af46e9f2...'
  )
```

### **Método 3: Via Code (Usado no projeto)**

```python
# apps/api/routes_vision_enrichment.py:429-442

# 1. Busca iterações
iters = AgenticIterDAO.get_iters(session, plan_id)

# 2. Coleta URLs do JSON
all_approved_urls = set()
for iteration in iters:
    all_approved_urls.update(iteration.get("approved_urls", []))

# 3. Busca detalhes em search_result
stmt = select(SearchResult).where(SearchResult.url.in_(all_approved_urls))
results = session.scalars(stmt)
```

---

## ✅ Proteção Contra Duplicatas Implementada

**Antes:**
```python
# ❌ Sempre cria novo
session.add(SearchResult(...))
```

**Agora:**
```python
# ✅ Verifica se existe
existing = session.query(SearchResult).filter_by(
    query_id=query_id, 
    url=url
).first()

if existing:
    # Atualiza
    existing.score = new_score
else:
    # Cria novo
    session.add(SearchResult(...))
```

---

## 🎯 Resultado

Agora, mesmo se o Agentic Search retornar a mesma URL em múltiplas iterações:
- ✅ **Não vai duplicar** na mesma query
- ✅ **Atualiza** o score/rank se a URL aparecer novamente
- ✅ **Mantém histórico** se aparecer em queries diferentes

**Problema resolvido!** 🎉

