# 🚀 Ativando GPT Inteligente - Quickstart

## 🎯 Objetivo
Fazer o GPT analisar SEU documento e sugerir as **melhores fontes** para aquele assunto específico.

---

## ⚡ **Ativação em 3 Passos**

### **1. Configure o .env**

Adicione esta linha ao arquivo `.env`:

```bash
USE_REAL_GPT_ALLOWLIST=true
```

Certifique-se de que já tem:
```bash
OPENAI_API_KEY=sk-...  # Sua chave OpenAI
```

### **2. Reinicie o Servidor**

```bash
# Ctrl+C no servidor atual
uvicorn apps.api.main:app --reload --port 8000
```

### **3. Teste!**

- Faça upload do PDF
- Clique "Rodar Pipeline"
- Veja os logs:

```json
{"event": "allowlist_calling_real_gpt", "model": "gpt-4o-mini"}
{"event": "allowlist_gpt_response_received", "response_len": 523}
{"event": "allowlist_plan_done", "domains": 10, "queries": 4}
```

**Pronto!** O GPT vai analisar o conteúdo e sugerir fontes relevantes.

---

## 📊 **Exemplos de Output**

### Seu PDF: "RAG Production-Ready"

**GPT vai sugerir:**
```json
{
  "goal": "Enriquecimento sobre RAG, LLMs e deployment em produção",
  "allow_domains": [
    "arxiv.org",
    "openai.com",
    "huggingface.co",
    "github.com",
    "python.langchain.com",
    "www.anthropic.com",
    "blog.llamaindex.ai",
    "docs.pinecone.io"
  ],
  "queries": [
    {
      "q": "site:arxiv.org RAG production deployment patterns",
      "why": "Papers científicos sobre arquiteturas de RAG em produção"
    },
    {
      "q": "LLM evaluation metrics production systems",
      "why": "Métricas e benchmarks de qualidade para sistemas de produção"
    },
    {
      "q": "vector database performance comparison 2024",
      "why": "Estudos comparativos atualizados de bancos vetoriais"
    }
  ]
}
```

### PDF sobre "Finanças Corporativas"

**GPT sugeriria:**
```json
{
  "allow_domains": [
    "investopedia.com",
    "cfainstitute.org",
    "hbr.org",
    "www.mckinsey.com",
    "deloitte.com",
    "scholar.google.com"
  ]
}
```

### PDF sobre "Machine Learning"

**GPT sugeriria:**
```json
{
  "allow_domains": [
    "arxiv.org",
    "papers.nips.cc",
    "jmlr.org",
    "github.com",
    "distill.pub",
    "paperswithcode.com"
  ]
}
```

---

## 🔍 **Como o GPT Decide**

O prompt instrui o GPT a:

1. **Analisar o domínio** (tecnologia, saúde, ciência, negócios, etc.)
2. **Identificar autoridades** no setor específico
3. **Sugerir fontes primárias** (papers, docs oficiais, estudos)
4. **Criar queries específicas** baseadas no conteúdo real
5. **Adaptar quality gates** (idade, tipos de doc)

---

## 💰 **Custo**

- **Por documento:** ~$0.001 (menos de 1 centavo!)
- **Token usage:** ~500-1000 tokens
- **Tempo:** ~2 segundos

---

## 🎯 **Diferença Visual**

### ANTES (Placeholder):
```
✅ Rápido, mas genérico
❌ Sempre sugere .gov.br
❌ Queries genéricas
```

### DEPOIS (GPT Real):
```
✅ Analisa SEU conteúdo
✅ Sugere fontes RELEVANTES ao tema
✅ Queries ESPECÍFICAS do documento
✅ Adapta gates por domínio
```

---

## ⚙️ **Configuração Completa (.env)**

```bash
# Ativar features
USE_REAL_GPT_ALLOWLIST=true  # ← Adicione esta!

# Credenciais (você já deve ter)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIzaSy...

# Opcional: Vision API (se quiser OCR premium)
USE_VISION_API=false  # Deixe false por enquanto (precisa Poppler)
```

---

## 🐛 **Breakpoint para Debug**

Se quiser ver o GPT funcionando:

**Arquivo:** `agentic/enrichment/gpt_allowlist_planner.py`  
**Linha:** 232 (logo antes da chamada)

```python
# Linha 232
logger.info("allowlist_calling_real_gpt", model=self.llm.model)
👆 BREAKPOINT AQUI

response = self.llm._call_chat_completion(...)
👆 BREAKPOINT AQUI (linha 245) - Ver resposta do GPT
```

---

**Adicione `USE_REAL_GPT_ALLOWLIST=true` no .env e teste! O GPT vai analisar SEU PDF de RAG e sugerir arxiv, OpenAI, HuggingFace, etc!** 🚀
