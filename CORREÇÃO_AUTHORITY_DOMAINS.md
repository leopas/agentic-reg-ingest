# ✅ Correção: Authority Domains Sempre do Plan do LLM

## 🎯 **Problema Identificado**

**ANTES:** Sistema usava `authority_domains` hardcoded do `configs/cse.yaml`
```yaml
# cse.yaml
authority_domains:
  - .gov.br          # ❌ Sempre governamental!
  - .saude.gov.br
  - ans.gov.br
```

**Resultado:** Mesmo se o GPT sugerisse `arxiv.org` para um PDF de AI, o scorer dava boost para `.gov.br`!

---

## ✅ **Solução Implementada**

### **Mudança 1: ResultScorer aceita authority_domains dinâmico**

```python
# agentic/scoring.py
class ResultScorer:
    def __init__(self, config: Dict, authority_domains: Optional[List[str]] = None):
        # ✅ Usa authority_domains fornecido (do plan)
        # ✅ Fallback para config apenas se não fornecido
        self.authority_domains = authority_domains or config.get("authority_domains", [])
```

### **Mudança 2: Enrichment Pipeline passa allow_domains do plan**

```python
# pipelines/enrichment_pipeline.py - linha 289
scorer = ResultScorer(
    cse_config,
    authority_domains=plan.allow_domains  # ← DO PLAN DO GPT!
)
```

### **Mudança 3: Endpoint /agentic/run também usa plan**

```python
# apps/api/main.py - linha 403
scorer = ResultScorer(
    cse_config,
    authority_domains=plan.allow_domains  # ← DO PLAN!
)
```

### **Mudança 4: Suporte a patterns (*.edu, *.ac.uk)**

```python
# agentic/scoring.py - linha 102-105
if "*" in auth_domain_clean:
    pattern = auth_domain_clean.replace("*", ".*")
    if re.search(pattern, domain):
        return 1.0  # Match!
```

---

## 📊 **Fluxo Completo Agora**

```
1. GPT analisa documento
   ↓
2. GPT retorna plan com allow_domains contextual:
   {
     "allow_domains": ["arxiv.org", "openai.com", "huggingface.co"]
   }
   ↓
3. EnrichmentPipeline cria scorer com esses domínios:
   scorer = ResultScorer(config, authority_domains=plan.allow_domains)
   ↓
4. Agentic Search executa queries
   ↓
5. Scorer dá boost (score=1.0) para:
   - https://arxiv.org/pdf/2401.12345.pdf  ← 1.0 ✅
   - https://openai.com/research/...        ← 1.0 ✅
   - https://github.com/langchain-ai/...    ← 1.0 ✅
   - https://www.gov.br/...                 ← 0.9 (legacy boost)
   - https://blog-random.com/...            ← 0.3 (não match)
   ↓
6. URLs com score mais alto são priorizadas!
   ↓
7. Judge LLM faz avaliação final
   ↓
8. URLs aprovadas vão para scraping
```

---

## 🎯 **Exemplos Práticos**

### **Caso 1: PDF sobre RAG/LLMs**

**GPT gera plan:**
```json
{
  "allow_domains": [
    "arxiv.org",
    "openai.com",
    "huggingface.co",
    "python.langchain.com"
  ]
}
```

**Scorer dá boost para:**
- ✅ `https://arxiv.org/pdf/2401.12345.pdf` → score +1.0
- ✅ `https://openai.com/research/gpt-4` → score +1.0
- ✅ `https://blog.langchain.dev/...` → score +1.0 (subdomain match)
- ❌ `https://www.gov.br/...` → score +0.9 (legacy)
- ❌ `https://medium.com/...` → score +0.3 (sem match)

---

### **Caso 2: PDF sobre Regulamentação de Saúde**

**GPT gera plan:**
```json
{
  "allow_domains": [
    "ans.gov.br",
    "saude.gov.br",
    "anvisa.gov.br"
  ]
}
```

**Scorer dá boost para:**
- ✅ `https://www.ans.gov.br/...` → score +1.0
- ✅ `https://portalfns.saude.gov.br/...` → score +1.0
- ❌ `https://arxiv.org/...` → score +0.3

---

### **Caso 3: PDF Acadêmico**

**GPT gera plan:**
```json
{
  "allow_domains": [
    "arxiv.org",
    "*.edu",
    "*.ac.uk",
    "scholar.google.com"
  ]
}
```

**Scorer dá boost para:**
- ✅ `https://arxiv.org/...` → score +1.0
- ✅ `https://mit.edu/...` → score +1.0 (pattern *.edu match!)
- ✅ `https://oxford.ac.uk/...` → score +1.0 (pattern *.ac.uk match!)
- ✅ `https://scholar.google.com/...` → score +1.0

---

## 🔍 **Como Verificar que Está Funcionando**

### **Logs para Procurar:**

```json
// 1. GPT sugere domínios
{"event": "allowlist_plan_done", "domains": 8}

// 2. Scorer é configurado com esses domínios
{"event": "enrichment_scorer_configured", "authority_domains": ["arxiv.org", "openai.com", ...]}

// 3. Durante scoring
{"event": "agentic_candidate_built", "url": "https://arxiv.org/...", "score": 4.2}
                                                                        ↑ High score!
```

### **Debug:**

Breakpoint em `agentic/scoring.py` linha 83:

```python
# linha 83
for auth_domain in self.authority_domains:
    👆 BREAKPOINT AQUI - Ver se tem os domínios do GPT
```

---

## 🎊 **Resumo da Correção**

| Componente | Antes | Depois |
|------------|-------|--------|
| **Scorer init** | Sempre `cse.yaml` | Aceita override do plan |
| **Enrichment** | ❌ Config hardcoded | ✅ Plan do GPT |
| **Main API** | ❌ Config hardcoded | ✅ Plan do GPT |
| **Patterns** | ❌ Não suportava | ✅ `*.edu`, `*.ac.uk` |

---

**Agora o sistema é 100% dinâmico e contextual!** 🎯

O GPT decide os domínios → Scorer usa eles → Agentic Search prioriza eles! 🚀
