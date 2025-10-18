# 🚀 Vertex AI Search - Setup Completo

## 🎯 **Por Que Vertex AI Search?**

### **CSE (Google Custom Search):**
- ✅ Simples de configurar
- ✅ Sem setup de infraestrutura
- ❌ Allowlist fixo (via query: site:domain.com)
- ❌ Limite: 10k queries/dia
- ❌ Não atualiza allowlist dinamicamente

### **Vertex AI Search (Discovery Engine):**
- ✅ **CRUD de allowlist on-the-fly** 🎯
- ✅ Datastore customizável
- ✅ Crawling automático de websites
- ✅ Ranking e personalização avançada
- ✅ Sem limite fixo (escalável)
- ❌ Setup inicial mais complexo
- ❌ Requer projeto GCP com billing

---

## 📋 **Setup em 5 Passos**

### **Passo 1: Criar Projeto GCP**

```bash
# Via console: https://console.cloud.google.com
# Ou via CLI:
gcloud projects create my-agentic-search --name="Agentic Search"
gcloud config set project my-agentic-search
```

### **Passo 2: Habilitar APIs**

```bash
gcloud services enable discoveryengine.googleapis.com
gcloud services enable storage.googleapis.com
```

### **Passo 3: Criar Datastore (Unstructured)**

```bash
# Via CLI
gcloud alpha discovery-engine data-stores create agentic-knowledge-base \
  --location=global \
  --industry-vertical=GENERIC \
  --content-config=NO_CONTENT \
  --solution-type=SOLUTION_TYPE_SEARCH \
  --project=my-agentic-search

# Ou via console:
# https://console.cloud.google.com/gen-app-builder
```

### **Passo 4: Adicionar Website Data Sources**

```bash
# Adicionar múltiplos domínios de uma vez
gcloud alpha discovery-engine data-stores update agentic-knowledge-base \
  --location=global \
  --add-web-crawling-sources=https://arxiv.org,https://openai.com,https://huggingface.co \
  --project=my-agentic-search

# Configurar padrões de inclusão/exclusão
gcloud alpha discovery-engine data-stores update agentic-knowledge-base \
  --location=global \
  --web-crawling-include-patterns="*.arxiv.org/*,*.openai.com/research/*" \
  --project=my-agentic-search
```

### **Passo 5: Configurar .env**

```bash
# .env
SEARCH_ENGINE=vertex

VERTEX_PROJECT_ID=my-agentic-search
VERTEX_DATASTORE_ID=agentic-knowledge-base
VERTEX_LOCATION=global

# Credenciais
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
```

---

## 🔧 **Instalação de Dependências**

```bash
pip install google-cloud-discoveryengine
```

---

## 🎯 **Como Funciona o CRUD de Allowlist Dinâmico**

### **Cenário: GPT sugere novos domínios**

```python
# 1. GPT analisa documento e retorna:
plan = {
    "allow_domains": [
        "arxiv.org",
        "openai.com",
        "anthropic.com"  # ← Novo domínio!
    ]
}

# 2. Sistema detecta domínio novo
existing_domains = get_datastore_domains()
new_domains = set(plan.allow_domains) - set(existing_domains)

if new_domains:
    # 3. Atualiza datastore automaticamente
    vertex_client.update_allowlist(new_domains)
    
    # 4. Trigger re-indexing
    vertex_client.trigger_reindex()

# 5. Próximas queries já incluem o novo domínio!
```

### **Implementação (Future Enhancement):**

```python
# agentic/vertex_search_client.py
def update_allowlist(self, domains: List[str]) -> bool:
    """Add domains to datastore dynamically."""
    from google.cloud import discoveryengine_v1 as discoveryengine
    
    # Update website data source
    for domain in domains:
        self.client.update_data_store(
            data_store=self.datastore_path,
            update_mask={"paths": ["web_crawling_config"]},
            data_store={
                "web_crawling_config": {
                    "include_patterns": [f"https://{domain}/*"]
                }
            }
        )
    
    logger.info("vertex_allowlist_updated", new_domains=len(domains))
    return True
```

---

## 📊 **Comparação: CSE vs Vertex AI**

| Feature | CSE | Vertex AI | Melhor |
|---------|-----|-----------|--------|
| **Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐ | CSE |
| **Allowlist Dinâmico** | ❌ | ✅ | Vertex |
| **Customização** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Vertex |
| **Custo (< 1k queries)** | Grátis | ~$0.02/query | CSE |
| **Custo (> 10k queries)** | $5/1k | ~$0.01/query | Vertex |
| **Qualidade Ranking** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Vertex |
| **Latência** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Vertex |

---

## 🎯 **Recomendação de Uso**

### **Use CSE quando:**
- ✅ Desenvolvimento/teste
- ✅ Budget limitado (< $50/mês)
- ✅ Allowlist é relativamente estático
- ✅ Menos de 10k queries/dia

### **Use Vertex AI quando:**
- ✅ Produção com escala
- ✅ Allowlist precisa ser atualizada dinamicamente pelo LLM
- ✅ Quer controle total sobre indexação
- ✅ Mais de 10k queries/dia
- ✅ Precisa de ranking customizado

---

## 🔄 **Migração CSE → Vertex (Zero Downtime)**

```bash
# 1. Configure Vertex AI (passos acima)

# 2. Teste em paralelo
SEARCH_ENGINE=vertex  # Apenas para testes

# 3. Se funcionar, mude para produção
# Não precisa mudar código, apenas .env!

# 4. Rollback se necessário
SEARCH_ENGINE=cse  # Volta para CSE
```

---

## 📝 **Exemplo de Configuração Completa**

### **.env para Vertex AI:**

```bash
# Search Engine
SEARCH_ENGINE=vertex

# Vertex AI
VERTEX_PROJECT_ID=my-project-123456
VERTEX_DATASTORE_ID=kb-agentic-sources
VERTEX_LOCATION=global

# Google Auth
GOOGLE_APPLICATION_CREDENTIALS=C:\secrets\gcp-service-account.json

# OpenAI (para GPT)
OPENAI_API_KEY=sk-...
USE_REAL_GPT_ALLOWLIST=true

# Outros
QDRANT_URL=http://localhost:6333
RAG_COLLECTION=kb_regulatory
```

---

## 🎊 **Benefícios da Implementação**

### **1. Abstração Completa:**
```python
# Código não precisa saber se é CSE ou Vertex!
search_client = create_search_client(config)
results = search_client.search_all(query, max_results=10)
```

### **2. Factory Pattern:**
```python
if SEARCH_ENGINE == "vertex":
    return VertexSearchClient(...)
else:
    return CSEClient(...)
```

### **3. Interface Unificada:**
Ambos implementam:
- `search(query, max_results)`
- `search_all(query, max_results, allow_domains)`

### **4. Configurável via .env:**
Mude apenas 1 variável:
```bash
SEARCH_ENGINE=vertex  # ou "cse"
```

---

## 🚀 **Quick Start**

### **Teste com CSE (atual):**
```bash
# .env
SEARCH_ENGINE=cse  # ou deixe vazio (default)
```

### **Migre para Vertex AI:**
```bash
# 1. Setup GCP (passos acima)
# 2. .env
SEARCH_ENGINE=vertex
VERTEX_PROJECT_ID=...
VERTEX_DATASTORE_ID=...

# 3. Instale
pip install google-cloud-discoveryengine

# 4. Teste!
```

---

## 📚 **Documentação Adicional**

- **Vertex AI Search:** https://cloud.google.com/generative-ai-app-builder/docs/introduction
- **Discovery Engine API:** https://cloud.google.com/discovery-engine/docs
- **Pricing:** https://cloud.google.com/generative-ai-app-builder/pricing

---

## 💡 **Futuras Melhorias**

- [ ] Implementar `update_allowlist()` real
- [ ] Auto-sync de domains do plan → datastore
- [ ] Cache de resultados do Vertex
- [ ] Metrics e observabilidade
- [ ] A/B testing CSE vs Vertex

---

**Sistema pronto para escalar de CSE para Vertex AI quando precisar!** 🎉

