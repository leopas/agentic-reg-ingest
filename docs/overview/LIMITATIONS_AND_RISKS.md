<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Limitations & Risks

Limitações conhecidas e estratégias de mitigação.

## ⚠️ Limitações Técnicas

### 1. Qualidade das Fontes

**Limitação:**
- Sites governamentais frequentemente têm:
  - PDFs escaneados (sem OCR)
  - Wrappers HTML complexos
  - Estrutura inconsistente
  - Links quebrados

**Impacto:**
- Chunks sem texto útil
- Falhas no type detection
- Re-routes excessivos

**Mitigação:**
- ✅ Magic bytes detection (prioridade alta)
- ✅ PDF wrapper detection
- ✅ Fallback multi-camada (readability → BeautifulSoup → LLM)
- ✅ Quality gates filtram PDFs vazios

### 2. HTML Pobre em Estrutura

**Limitação:**
- Páginas HTML sem headings (H1-H3)
- Texto corrido sem "Art.", "Anexo"
- Tabelas em imagens

**Impacto:**
- Chunking sem anchors (menos citável)
- Score de anchor baixo (pode rejeitar)

**Mitigação:**
- ✅ Fallback token-aware (funciona sem anchors)
- ✅ `min_anchor_signals: 0` para HTMLs
- ✅ LLM structure extraction (extrai seções)

### 3. Viés e Erro de LLM

**Limitação:**
- **Planner** pode gerar queries irrelevantes
- **Judge** pode rejeitar documento bom
- **Inference mode** pode "alucinar"

**Impacto:**
- Falsos negativos (rejeita norma útil)
- Custos desnecessários (queries ruins)
- Respostas imprecisas

**Mitigação:**
- ✅ Quality gates **hard-coded** (antes do judge)
- ✅ Grounded mode (sem inferência)
- ✅ Budget limits (max_cse_calls, max_iterations)
- ✅ Human-in-the-loop (review plan antes de executar)
- ✅ Audit trail (toda decisão registrada)

---

## 💰 Custos e Limites

### API Costs

| Serviço | Custo | Limite Sugerido |
|---------|-------|-----------------|
| Google CSE | $5/1000 queries | max_cse_calls: 60 |
| OpenAI GPT-4o-mini | $0.15/1M tokens | max_queries_per_iter: 2 |
| Embeddings 3-small | $0.02/1M tokens | batch_size: 64 |

**Estimativa mensal (uso moderado):**
- Agentic Search: 10 planos/mês × $0.50 = **$5.00**
- Embeddings: 500k tokens/mês = **$0.01**
- CSE: 100 queries/mês = **$0.50**
- **Total: ~$6/mês**

### Rate Limits

**Google CSE:**
- Free tier: 100 queries/dia
- Paid: $5/1000 queries

**OpenAI:**
- GPT-4o-mini: 30k requests/min
- Embeddings: 3k requests/min

**Mitigação:**
- ✅ Cache TTL (evita queries duplicadas)
- ✅ Budget configs (max_cse_calls)
- ✅ Retry com backoff

---

## 🔒 Privacidade e Segurança

### 1. Dados Enviados a Provedores Externos

**O que vai para OpenAI:**
- ✅ Texto de documentos públicos (RNs, Leis)
- ✅ Prompts de usuário (chat)
- ✅ Trechos recuperados (RAG context)

**⚠️ NÃO envie:**
- ❌ Documentos confidenciais
- ❌ Dados pessoais/sensíveis (LGPD)
- ❌ Segredos comerciais

**Mitigação:**
- ✅ Use LLM local (LM Studio/Ollama) para dados sensíveis
- ✅ Allowlist de domínios (só fontes públicas)
- ✅ Deny patterns (bloqueia URLs sensíveis)
- ✅ Redact PII antes de chunking (se necessário)

### 2. Injection Attacks

**Vetor:**
- HTML malicioso em URL aprovada
- PDF com scripts embarcados

**Impacto:**
- XSS via payload no Qdrant
- Code execution no parsing

**Mitigação:**
- ✅ Sanitização de HTML (readability strip scripts)
- ✅ PDF parsing seguro (pdfplumber, pypdf)
- ✅ Escape de payload no Qdrant
- ✅ CSP headers na UI

### 3. Dependências Vulneráveis

**Risco:**
- Bibliotecas com CVEs conhecidos

**Mitigação:**
- ✅ Dependabot (GitHub)
- ✅ `pip-audit` em CI
- ✅ Política de atualização (mensal)

---

## 📉 Limitações de Escala

### Volume de Documentos

**Atual:**
- MySQL: ~100k documentos ok
- Qdrant: ~1M chunks ok
- Search cache: TTL 30 dias

**Bottlenecks:**
- Embeddings: ~100 docs/min (API limit)
- Chunking: ~20 PDFs/min (CPU-bound)

**Escalabilidade:**
- ✅ Horizontal (múltiplos workers para ingest)
- ✅ Batch embeddings (até 2048 texts/request)
- ✅ Qdrant sharding (se > 10M pontos)

### Precisão do RAG

**Limitações:**
- Top-K fixo (não adaptativo)
- Sem re-ranking (cross-encoder)
- Sem hybrid search (sparse+dense)

**Impacto:**
- Pode perder documento relevante fora do top-8
- Recall não otimizado para queries longas

**Mitigação (roadmap):**
- 🔄 Implementar re-ranking
- 🔄 Hybrid search (BM25 + embeddings)
- 🔄 Query expansion automática

---

## ⚖️ Considerações Legais

### Uso de Dados Públicos

**Ok:**
- ✅ Documentos oficiais gov.br (domínio público)
- ✅ Respeitar robots.txt
- ✅ Rate limiting (evitar sobrecarga)

**Atenção:**
- ⚠️ Termos de uso da ANS/TISS
- ⚠️ Atribuição de fonte (sempre citar URL)
- ⚠️ Não redistribuir como produto primário

### LGPD (se aplicável)

**Se processar dados pessoais:**
- Base legal: legítimo interesse (melhoria operacional)
- Minimização: só campos necessários
- Transparência: política de privacidade
- Direitos: acesso, retificação, exclusão

**Nota:** Para documentos públicos regulatórios (sem PII), LGPD não se aplica diretamente.

---

## 🎯 Quando NÃO Usar Este Sistema

❌ **Documentos confidenciais** (sem LLM local configurado)  
❌ **Dados pessoais sensíveis** (LGPD/HIPAA)  
❌ **Busca genérica web** (use search engine tradicional)  
❌ **Volumes extremos** (>10M docs sem sharding)  
❌ **Latência crítica** (<100ms SLA) - RAG tem overhead

---

## 📋 Responsabilidades do Usuário

### Operador do Sistema

**Deve:**
- ✅ Configurar quality gates adequados
- ✅ Revisar planos gerados (especialmente deny_patterns)
- ✅ Monitorar custos (CSE, LLM)
- ✅ Manter credenciais seguras (.env)
- ✅ Fazer backups (DB e Qdrant)

**Não deve:**
- ❌ Aprovar documentos sem revisar audit trail
- ❌ Desabilitar quality gates em produção
- ❌ Expor API sem autenticação (se público)
- ❌ Ignorar violations reportados

### Consumidor do RAG

**Deve:**
- ✅ Verificar fontes citadas
- ✅ Usar grounded mode para citações oficiais
- ✅ Entender limitações do inference mode
- ✅ Validar respostas críticas manualmente

**Não deve:**
- ❌ Confiar 100% em inference sem validação
- ❌ Usar para decisões críticas sem review humano
- ❌ Redistribuir respostas como "oficial"

---

## 🔬 Avaliação Contínua

Ver [RAG Evaluation Plan](../rag/EVALUATION_PLAN.md) para métricas e testes.

**Métricas a monitorar:**
- Precisão de citações (groundedness)
- Taxa de aprovação (approved/total candidates)
- Cobertura de normas (% do corpus oficial)
- Custo por query ($/approved doc)
- Latência (p50, p95, p99)

---

[← Back to Use Cases](USE_CASES.md) | [Architecture →](../architecture/ARCHITECTURE.md)

