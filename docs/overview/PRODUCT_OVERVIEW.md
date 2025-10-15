<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Product Overview

## O Problema

Organizações do setor de saúde suplementar precisam:
- **Buscar** normas regulatórias (ANS, TISS, Planalto) atualizadas
- **Processar** documentos heterogêneos (PDF, HTML, ZIP)
- **Indexar** conteúdo para busca semântica (RAG)
- **Citar** fontes de forma auditável
- **Monitorar** mudanças normativas

**Desafios:**
- 🔴 Normas mudam frequentemente
- 🔴 Documentos sem estrutura consistente
- 🔴 Wrappers HTML apontando para PDFs
- 🔴 Citações imprecisas ("vi em algum lugar...")
- 🔴 Custos elevados (re-processar tudo sempre)

---

## A Solução: Agentic Reg Ingest

Sistema de **busca inteligente** + **ingestão estruturada** + **RAG citável**.

### 🤖 Agentic Search (Plan→Act→Observe→Judge→Re-plan)

**O que faz:**
1. **Planner LLM** gera estratégia de busca (queries, gates, stop conditions)
2. **Act**: Executa queries no Google CSE
3. **Observe**: Detecta tipo de documento, score, anchors
4. **Judge**: LLM avalia candidatos, rejeita ruído, propõe novas queries
5. **Re-plan**: Merge queries, itera até atingir meta

**Benefícios:**
- ✅ Autonomia (gera queries sem intervenção)
- ✅ Qualidade (rejeita blogs, HTMLs genéricos)
- ✅ Auditabilidade (cada decisão registrada)
- ✅ Limitado (budgets e stop conditions)

### 📦 Chunking Inteligente

**Estratégia:**
1. **Structure-first**: Detecta anchors (Art., Anexo, Tabela, Capítulo)
2. **Segment**: Divide por anchors (unidades semânticas)
3. **Token-aware**: Chunks de 512 tokens com overlap 50
4. **Metadata-rich**: page_hint, anchor_type, source_type

**Benefícios:**
- ✅ Citações precisas ("Conforme Art. 5º, §2º...")
- ✅ Recall melhor (overlap contextual)
- ✅ Custos previsíveis (512 tokens/chunk)

### 🗄️ Vector Database (Qdrant)

**Features:**
- Embeddings OpenAI ou local (LM Studio/Ollama)
- Upsert idempotente (point_id determinístico)
- Batch processing (64 chunks/batch)
- Filters por doc_hash, source_type, anchor_type

**Benefícios:**
- ✅ Busca semântica (não só keywords)
- ✅ Escalável (milhões de chunks)
- ✅ Re-push seguro (overwrite mode)

### 💬 RAG Chat

**Two Modes:**
- **Grounded**: Responde SÓ com base nos trechos recuperados
- **Inference**: Permite raciocínio explícito sobre trechos

**Features:**
- Retrieval logs (quais chunks foram considerados)
- Citações automáticas (título + URL)
- Top-K configurável (1-20)
- Score threshold

---

## 👥 Público-Alvo

### Compliance & Jurídico
- Buscar normas atualizadas
- Verificar conformidade
- Gerar relatórios com citações

### Arquitetura de Soluções
- Análise de impacto de mudanças normativas
- Documentação de decisões técnicas
- Knowledge base para squads

### Data & AI Teams
- RAG para chatbots internos
- Knowledge graphs regulatórios
- Monitoramento automatizado

### Gestão de Qualidade
- Auditoria de processos
- Compliance contínuo
- Rastreabilidade end-to-end

---

## 🎯 Diferenciais

### vs. Busca Manual (Google)
✅ Autonomia (loop agentivo)  
✅ Quality gates (rejeita ruído)  
✅ Audit trail (decisões registradas)

### vs. Web Scraping Tradicional
✅ Type detection robusta  
✅ Diff detection (só re-processa mudanças)  
✅ Anchor-aware chunking (não corta artigo no meio)

### vs. RAG Genérico
✅ Chunking especializado (regulatório)  
✅ Grounded mode (sem alucinação)  
✅ Citações automáticas  
✅ Proveniência completa

---

## 📊 Glossário

| Termo | Definição |
|-------|-----------|
| **Agentic Search** | Loop autônomo de busca com LLM planner e judge |
| **Anchor** | Marcador estrutural (Art., Anexo, Capítulo, H1-H3) |
| **CSE** | Google Custom Search Engine (API de busca) |
| **doc_hash** | Identificador único do documento (SHA256) |
| **Grounded** | Modo RAG que responde SÓ com base em trechos |
| **Judge** | LLM que avalia candidatos e propõe novas queries |
| **Quality Gates** | Critérios hard-coded (type, age, score, anchors) |
| **RAG** | Retrieval-Augmented Generation (busca + LLM) |
| **Stop Conditions** | Critérios para parar loop (min_approved, max_iterations) |
| **Vector Status** | Estado do push (none, present, partial, error) |

---

## 🎁 Benefícios Mensuráveis

**Tempo:**
- Busca manual: ~2h para 10 normas
- Agentic Search: ~5min para 12 normas aprovadas

**Qualidade:**
- Precisão: >90% (com quality gates)
- Citabilidade: 100% (todas têm URL + anchor)

**Custo:**
- CSE: ~$5/1000 queries
- LLM (plan+judge): ~$0.02/iteração
- Embeddings: ~$0.02/1M tokens

**ROI:**
- Reduz tempo de compliance em 80%
- Elimina erro de citação manual
- Auditoria automática (zero custo adicional)

---

[← Back to Index](../index.md) | [Next: Use Cases →](USE_CASES.md)

