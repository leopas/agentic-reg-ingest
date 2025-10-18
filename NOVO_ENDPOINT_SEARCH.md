# 🚀 Novo Endpoint `/search` - Unified Search API

## ✅ **IMPLEMENTADO COMPLETO!**

---

## 📋 **Especificação**

### **Endpoint:** `POST /search`

### **Request Body:**
```json
{
  "q": "RAG production deployment",
  "include_domains": ["arxiv.org", "openai.com", "huggingface.co"],
  "exclude_domains": ["spam.com", "ads.com"],
  "provider": "pse",
  "page": 1,
  "page_size": 10
}
```

### **Response:**
```json
{
  "results": [
    {
      "url": "https://arxiv.org/pdf/2401.12345.pdf",
      "title": "RAG in Production: Best Practices",
      "snippet": "This paper presents...",
      "html_snippet": "This <b>paper</b> presents..."
    }
  ],
  "total_results": 1234,
  "page": 1,
  "page_size": 10,
  "provider": "pse",
  "cache_hit": false
}
```

---

## 🎯 **Features Implementadas**

### ✅ **1. Provider Selection**
```python
provider: "pse" | "vertex" | null (default)
```

- **pse**: Google Programmable Search Engine
  - Allow-list dinâmico **por requisição**
  - Usa `site:` operator
  - Sem necessidade de atualizar configuração

- **vertex**: Vertex AI Search (Discovery Engine)
  - Allow-list gerenciada via API
  - Atualiza estado do índice
  - Requer setup de datastore

- **null**: Usa default do `.env` (`SEARCH_ENGINE`)

### ✅ **2. Dynamic Allow-List (PSE)**
```json
{
  "include_domains": ["arxiv.org", "openai.com"],
  "exclude_domains": ["spam.com"]
}
```

**Query gerada:**
```
"RAG production" (site:arxiv.org OR site:openai.com) -site:spam.com
```

### ✅ **3. Cache LRU (In-Memory)**
- **Size:** 1000 entries (configurável via `SEARCH_CACHE_SIZE`)
- **TTL:** 1 hora (configurável via `SEARCH_CACHE_TTL`)
- **Key:** hash(provider + query + domains + page)
- **Eviction:** LRU simples

**Logs:**
```json
{"event": "cache_hit", "key": "a1b2c3..."}
{"event": "cache_set", "key": "a1b2c3..."}
```

### ✅ **4. Rate Limiting & Backoff**
```python
# PSE: Throttle configurable
PSE_THROTTLE_QPS=1.0  # 1 query por segundo

# Retry com exponential backoff
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=retry_if_exception_type(HTTPError),
)
```

### ✅ **5. Domain Sanitization**
```python
# Input
["https://arxiv.org/", "WWW.OpenAI.COM", "github.com/"]

# After sanitization
["arxiv.org", "openai.com", "github.com"]

# Remove: protocol, www, trailing slash, duplicates
```

### ✅ **6. Fallback Automático**
```python
if provider not in providers:
    logger.warning("Falling back to first available")
    provider = providers[0]
```

---

## 🔧 **Configuração**

### **.env:**
```bash
# Provider padrão
SEARCH_ENGINE=pse  # ou "vertex"

# PSE (Google Custom Search)
GOOGLE_API_KEY=AIzaSy...
GOOGLE_CX=your_cx_id
PSE_THROTTLE_QPS=1.0

# Vertex AI Search
VERTEX_PROJECT_ID=my-project
VERTEX_DATASTORE_ID=kb-sources
VERTEX_LOCATION=global

# Cache
SEARCH_CACHE_SIZE=1000
SEARCH_CACHE_TTL=3600
```

---

## 📡 **Endpoints Criados**

### **1. POST /search** (Principal)
Busca unificada com provider selection.

### **2. GET /search/providers** (Info)
Lista providers disponíveis.

**Response:**
```json
{
  "providers": ["pse"],
  "default": "pse",
  "status": {
    "pse": "available"
  }
}
```

---

## 🎯 **Uso via API**

### **Exemplo 1: PSE com Dynamic Allow-List**

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "q": "RAG production deployment",
    "include_domains": ["arxiv.org", "openai.com", "huggingface.co"],
    "provider": "pse",
    "page": 1,
    "page_size": 10
  }'
```

**Query real enviada ao Google:**
```
RAG production deployment (site:arxiv.org OR site:openai.com OR site:huggingface.co)
```

### **Exemplo 2: Vertex AI Search**

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "q": "machine learning best practices",
    "include_domains": ["arxiv.org"],
    "provider": "vertex"
  }'
```

### **Exemplo 3: Default Provider**

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "q": "kubernetes deployment",
    "include_domains": ["kubernetes.io", "cloud.google.com"]
  }'
```

Usa provider definido em `SEARCH_ENGINE` no `.env`.

---

## 🏗️ **Arquitetura**

```
┌──────────────────────────────────────────────┐
│         POST /search (Endpoint)              │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│      SearchService (Orchestrator)            │
│  - Provider selection                        │
│  - Cache check (LRU)                         │
│  - Fallback logic                            │
└────────────┬──────────────┬──────────────────┘
             │              │
             ▼              ▼
┌─────────────────┐  ┌─────────────────┐
│  PSEProvider    │  │ VertexProvider  │
│                 │  │                 │
│ - site: ops     │  │ - Filter API    │
│ - Throttle QPS  │  │ - Datastore     │
│ - Retry 3x      │  │ - Retry 3x      │
└─────────────────┘  └─────────────────┘
         │                    │
         ▼                    ▼
┌──────────────────────────────────────────────┐
│       Google APIs (CSE vs Vertex)            │
└──────────────────────────────────────────────┘
```

---

## 📊 **Diferença: PSE vs Vertex**

| Feature | PSE | Vertex AI |
|---------|-----|-----------|
| **Allow-list** | ✅ Dinâmico por chamada | ⚠️ Gerenciado (estado do índice) |
| **Setup** | ⭐⭐⭐⭐⭐ Simples | ⭐⭐ Complexo |
| **Cost** | $5/1k queries | ~$0.01/query |
| **Customização** | ⭐⭐ Limitado | ⭐⭐⭐⭐⭐ Total |
| **Latência** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Quota** | 10k/dia | Sem limite fixo |

---

## 🎯 **Integração com Vision Enrichment**

O pipeline de enrichment agora usa automaticamente o novo sistema:

```python
# enrichment_pipeline.py
search_service = get_search_service()

# GPT gera plan com allow_domains
plan = gpt_planner.plan(jsonl_path)

# Busca com allow-list do GPT
results = search_service.search(
    SearchRequest(
        q=query,
        include_domains=plan.allow_domains,  # ← Do GPT!
        provider="pse",  # ou "vertex"
    )
)
```

---

## 💾 **Cache Strategy**

### **Key:**
```python
cache_key = SHA256(provider + query + include_domains + exclude_domains + page)
```

### **Storage:**
```
In-Memory LRU (padrão)
├── Max 1000 entries
├── TTL 1 hora
└── Eviction: oldest first

Redis (futuro)
├── Shared across instances
├── Persistent
└── Scalable
```

---

## 🔒 **Rate Limiting**

### **PSE:**
```python
# Throttle por QPS
PSE_THROTTLE_QPS=1.0  # 1 query/segundo

# Sleep automático entre requests
if elapsed < throttle_delay:
    sleep(throttle_delay - elapsed)
```

### **Retry Policy:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry_if_exception_type=(Timeout, HTTPError),
)
```

**Backoff:**
- Tentativa 1: imediato
- Tentativa 2: 4s depois
- Tentativa 3: 8s depois

---

## 📚 **Arquivos Criados**

```
agentic/providers/
├── __init__.py
├── base.py               # Interface abstrata
├── pse_provider.py       # PSE implementation
└── vertex_provider.py    # Vertex implementation

agentic/
└── search_service.py     # Orchestrator + Cache

apps/api/
└── routes_search.py      # REST endpoints

docs/
└── NOVO_ENDPOINT_SEARCH.md  # Esta documentação
```

---

## 🚀 **Quick Test**

### **1. Reinicie o servidor:**
```bash
uvicorn apps.api.main:app --reload --port 8000
```

### **2. Teste o endpoint:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "q": "machine learning",
    "include_domains": ["arxiv.org"],
    "page_size": 5
  }'
```

### **3. Veja providers disponíveis:**
```bash
curl http://localhost:8000/search/providers
```

---

## 🎊 **Benefícios da Nova Arquitetura**

| Antes | Depois |
|-------|--------|
| CSE hardcoded | ✅ PSE ou Vertex configurável |
| Allow-list fixo | ✅ Dinâmico por requisição |
| Sem cache | ✅ Cache LRU |
| Sem rate limit | ✅ Throttle + backoff |
| Sem sanitização | ✅ Domain sanitization |
| 1 provider | ✅ Factory pattern extensível |

---

**Sistema agora é enterprise-grade com provider abstraction completo!** 🚀

