<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 💬 Chat RAG Guide

Guia completo para usar o Chat RAG sobre a knowledge base `kb_regulatory`.

## 🎯 URL de Acesso

```
http://localhost:8000/chat
```

## 🚀 Iniciar Chat

### 1. Certifique-se que tem chunks no VectorDB

```bash
# Via UI Agentic Console
http://localhost:8000/ui
→ Aprovar documentos
→ Rechunk
→ Push to Vector

# Ou via API diretamente
curl -X POST http://localhost:8000/vector/push \
  -H "Content-Type: application/json" \
  -d '{"doc_hashes":["abc123..."], "collection":"kb_regulatory"}'
```

### 2. Inicie o servidor

```bash
make api
# ou
uvicorn apps.api.main:app --reload
```

### 3. Abra o Chat

```
http://localhost:8000/chat
```

---

## 🎨 Interface do Chat

### Painel Esquerdo: Pergunta + Resposta

**Configurações:**
- **Modo de resposta:**
  - 🎯 **Grounded** - Somente baseado nos trechos (não inventa)
  - 🧠 **Inferência** - Permite raciocínio (marca inferências)
- **Top-K:** Quantos chunks recuperar (1-20)
- **Score mínimo:** Filtro de relevância (0.0-1.0)

**Entrada:**
- Textarea para pergunta
- Botão "🚀 Perguntar"
- Atalho: **Ctrl+Enter** para enviar

**Saída:**
- Resposta humanizada em português
- Seção "Fontes consideradas"
- Citações quando aplicável

### Painel Direito: Logs de Retrieval

**Tabela com:**
- **Status** - Badge "USADO" (verde) para chunks no contexto
- **Doc Hash** - Primeiros 12 chars
- **Chunk ID** - Identificador do chunk
- **Score** - Relevância (0.000-1.000)
- **Título** - Nome do documento
- **URL** - Link clicável
- **Tipo** - pdf/html/zip
- **Anchor** - Art., Anexo, Tabela, etc.

---

## 💡 Exemplos de Perguntas

### Grounded Mode (Factual)

```
Quais são os prazos máximos de atendimento para consultas 
médicas definidos pela RN 259 da ANS?
```

**Resposta esperada:**
```
De acordo com a RN 259/2011, os prazos máximos são:

- Consulta básica: 7 dias úteis
- Consulta especializada: 14 dias úteis
- Consulta em pronto-atendimento: atendimento imediato

Fontes consideradas:
- Resolução Normativa 259/2011 - ANS
  https://www.gov.br/ans/.../rn-259.pdf
- Anexo II - Prazos de Atendimento
```

### Inference Mode (Raciocínio)

```
Com base nas normas da ANS, uma operadora pode ser multada 
por atraso no atendimento de consultas?
```

**Resposta esperada:**
```
Sim. Pela combinação dos documentos recuperados, infere-se que:

A RN 259 estabelece prazos máximos obrigatórios. O não cumprimento 
configura infração sanitária (Lei 9.656/98, Art. 25).

A ANS pode aplicar:
- Advertência
- Multa pecuniária
- Suspensão de comercialização

[INFERÊNCIA]: A recorrência pode levar à suspensão do registro 
da operadora, embora isso dependa de análise caso a caso.

Fontes consideradas:
- RN 259/2011 (prazos)
- Lei 9.656/98 (sanções)
- RN 395/2016 (fiscalização)
```

---

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

```bash
# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# RAG
RAG_COLLECTION=kb_regulatory

# LLM
OPENAI_API_KEY=sk-proj-...
OPENAI_BASE_URL=  # Opcional: LM Studio/Ollama
OPENAI_MODEL=gpt-4o-mini  # ou gpt-4, etc.

# Embeddings
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBED_DIM=1536
```

### Top-K Recomendado

| Tipo de Pergunta | Top-K | Score Mínimo |
|------------------|-------|--------------|
| Factual simples | 3-5 | 0.75 |
| Comparação | 8-10 | 0.70 |
| Exploratória | 12-15 | 0.65 |
| Abrangente | 15-20 | 0.60 |

### Quando usar cada Modo

**Grounded (🎯):**
- ✅ Perguntas factuais
- ✅ Citações regulatórias
- ✅ Auditorias/compliance
- ✅ Quando precisa **provar** a resposta

**Inferência (🧠):**
- ✅ Análises comparativas
- ✅ "E se..." / cenários
- ✅ Sínteses de múltiplas normas
- ✅ Quando quer **insights** além do literal

---

## 📊 Como Funciona (Por Baixo dos Panos)

### 1. User Input
```
Pergunta: "Quais prazos de consulta?"
Mode: grounded
Top-K: 8
```

### 2. Embedding Query
```python
from embeddings.encoder import encode_texts
query_vector = encode_texts(["Quais prazos de consulta?"])[0]
# → [0.123, -0.456, 0.789, ..., 1536 dims]
```

### 3. Qdrant Search
```python
from qdrant_client import QdrantClient
client.search(
    collection_name="kb_regulatory",
    query_vector=query_vector,
    limit=8,
)
# → Returns top 8 chunks by cosine similarity
```

### 4. Context Formation
```python
# Select best 3-6 chunks for context (avoid token overflow)
context_chunks = hits[:6]

# Format context
context = """
[Trecho 1] RN 259/2011 (relevância=0.92)
URL: https://...
---
Art. 2º - Os prazos máximos para consulta médica...

[Trecho 2] Anexo II (relevância=0.87)
URL: https://...
---
Tabela de Prazos:
- Consulta básica: 7 dias úteis
...
"""
```

### 5. LLM Call (Grounded)
```python
from openai import OpenAI

system = "Você é especialista ANS. Responda SOMENTE com trechos."
user = f"[PERGUNTA] {question}\n\n[TRECHOS]\n{context}\n\nRegras: ..."

response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.0,  # Determinístico
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
)

answer = response.choices[0].message.content
```

### 6. Return to User
```json
{
  "answer": "De acordo com a RN 259...\n\nFontes: ...",
  "used": [chunk1, chunk2],  // Usados no contexto
  "log": [chunk1, ..., chunk8]  // Todos recuperados
}
```

---

## 🎯 Qualidade das Respostas

### Fatores que Influenciam

**1. Qualidade dos Chunks:**
- ✅ Chunks com anchors (Art., Anexo) → melhor citação
- ✅ Chunks de PDFs oficiais → maior confiança
- ✅ Chunks recentes → informação atualizada

**2. Relevância (Score):**
- **> 0.85** - Muito relevante (quase certo que contém resposta)
- **0.70-0.85** - Relevante (provavelmente útil)
- **0.60-0.70** - Moderado (pode ter contexto)
- **< 0.60** - Baixo (provavelmente não relevante)

**3. Top-K:**
- **Baixo (3-5)** - Respostas focadas, rápidas
- **Médio (8-12)** - Balanceado
- **Alto (15-20)** - Respostas abrangentes, mais lento

---

## 🚨 Troubleshooting

### Resposta: "Não encontrei informação suficiente"

**Causas:**
- ❌ Nenhum chunk relevante (score muito baixo)
- ❌ Pergunta muito específica/fora do escopo
- ❌ Chunks ainda não foram indexados

**Soluções:**
```bash
# 1. Verificar se tem chunks no Qdrant
curl http://localhost:6333/collections/kb_regulatory

# 2. Diminuir score_threshold
# Score mínimo: (deixar vazio ou 0.5)

# 3. Aumentar Top-K
# Top-K: 15

# 4. Reformular pergunta (mais genérica)
```

### Resposta em branco ou erro

**Debug:**
```bash
# 1. Verificar logs do servidor
tail -f logs/api.log | grep "rag_"

# 2. Verificar embeddings
python -c "from embeddings.encoder import encode_texts; print(len(encode_texts(['test'])[0]))"

# 3. Verificar Qdrant
curl http://localhost:6333/collections/kb_regulatory/points/scroll \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 3}'
```

### Chunks não aparecem nos Logs

**Causa:** Collection vazia ou nome errado

**Solução:**
```bash
# Verificar collections disponíveis
curl http://localhost:6333/collections

# Verificar count
curl http://localhost:6333/collections/kb_regulatory
# → "points_count": 0 ❌ (precisa fazer push)

# Push chunks
http://localhost:8000/ui
→ Documentos Aprovados
→ Selecionar
→ Push to Vector
```

---

## 📝 Dicas de Uso

### 1. Perguntas Efetivas

**✅ BOM:**
```
Quais documentos a operadora deve enviar na DIOPS?
Qual o prazo para atendimento em urgência/emergência?
Como funciona a cobertura para exames de alta complexidade?
```

**❌ EVITAR:**
```
Me conta tudo sobre a ANS  (muito genérico)
Quanto custa um plano de saúde?  (fora do escopo regulatório)
```

### 2. Modo Grounded vs. Inferência

**Use Grounded quando:**
- Precisa de citação exata
- Auditoria/compliance
- Resposta oficial para terceiros

**Use Inferência quando:**
- Análise de impacto
- Comparação de normas
- Síntese de múltiplos documentos

### 3. Verificar Fontes

**Sempre cheque:**
- ✅ URLs das fontes (clique para validar)
- ✅ Scores (>0.75 = alta confiança)
- ✅ Tipos (PDF oficial > HTML genérico)
- ✅ Anchors (Art. 5º > texto sem estrutura)

---

## 🎁 Recursos Adicionais

### Navegação

```
http://localhost:8000/          → Root (lista endpoints)
http://localhost:8000/ui        → Agentic Console
http://localhost:8000/chat      → RAG Chat ← VOCÊ ESTÁ AQUI
http://localhost:8000/docs      → API Docs (Swagger)
```

### Links Rápidos no Chat

- **← Voltar para Agentic Console** - Link no header
- **API Docs** - Swagger para endpoints

### API Direta

Você também pode usar via cURL/Postman:

```bash
curl -X POST http://localhost:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais prazos de consulta?",
    "mode": "grounded",
    "top_k": 8,
    "score_threshold": 0.7,
    "collection": "kb_regulatory"
  }'
```

---

## 🎉 RESUMO

**✅ Chat RAG Completo:**
- Retrieval via Qdrant (embeddings)
- Two modes (grounded/inference)
- Logs de chunks considerados
- UI humanizada (HTMX)
- Integrado ao pipeline existente

**✅ Pronto para usar!**

**URL:** `http://localhost:8000/chat`

**DIVIRTA-SE PERGUNTANDO! 💬✨🚀**

