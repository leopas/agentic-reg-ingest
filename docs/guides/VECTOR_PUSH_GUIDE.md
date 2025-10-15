<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 🚀 Vector Push Guide

Guia completo para enviar chunks ao Qdrant VectorDB com embeddings.

## 📋 Overview

O endpoint `/vector/push` permite enviar chunks processados para o Qdrant, gerando embeddings e fazendo upsert idempotente.

## 🔧 Configuração

### Variáveis de Ambiente

Adicione ao seu `.env`:

```bash
# Embeddings Configuration
EMBED_PROVIDER=openai              # Options: openai, azure, local
OPENAI_API_KEY=sk-...              # Your OpenAI API key
OPENAI_BASE_URL=                   # Optional: for LM Studio/Ollama (e.g., http://localhost:1234/v1)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBED_DIM=1536                     # Must match model: ada-002=1536, 3-small=1536, 3-large=3072

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=                    # Optional: leave empty for local Qdrant
```

### Modelos Suportados

| Modelo | Dimensão | Provider | Custo (USD/1M tokens) |
|--------|----------|----------|----------------------|
| `text-embedding-ada-002` | 1536 | OpenAI | $0.10 |
| `text-embedding-3-small` | 1536 | OpenAI | $0.02 |
| `text-embedding-3-large` | 3072 | OpenAI | $0.13 |
| Local (LM Studio/Ollama) | Variável | Local | Grátis |

## 📡 API Endpoints

### POST /vector/push

Envia chunks para o VectorDB com embeddings.

**Request:**
```json
{
  "doc_hashes": ["abc123...", "def456..."],
  "collection": "kb_regulatory",
  "overwrite": false,
  "batch_size": 64
}
```

**Parâmetros:**
- `doc_hashes` (obrigatório) - Lista de hashes dos documentos
- `collection` - Nome da coleção no Qdrant (default: `kb_regulatory`)
- `overwrite` - Se `true`, apaga pontos existentes antes (default: `false`)
- `batch_size` - Tamanho do lote para upsert (default: `64`)

**Response:**
```json
{
  "pushed": 128,
  "skipped": 0,
  "collection": "kb_regulatory"
}
```

### POST /vector/delete

Remove chunks do VectorDB.

**Request:**
```json
{
  "doc_hashes": ["abc123..."],
  "collection": "kb_regulatory"
}
```

**Response:**
```json
{
  "deleted": 64,
  "collection": "kb_regulatory"
}
```

## 🎯 Fluxo Completo

### 1. Gerar/Aprovar Documentos

Via Agentic Search ou manualmente:
```bash
# Agentic Search
make agentic-html

# Resultado: documentos aprovados em search_result
```

### 2. Regenerar Chunks

```bash
curl -X POST http://localhost:8000/ingest/regenerate \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.gov.br/ans/.../rn-259.pdf"],
    "overwrite": true
  }'
```

**Resultado:**
- ✅ Chunks salvos em `chunk_store`
- ✅ Manifest atualizado (`status=done`, `chunk_count=15`)
- ✅ `vector_status=none` (ainda não enviado)

### 3. Push para VectorDB

```bash
curl -X POST http://localhost:8000/vector/push \
  -H "Content-Type: application/json" \
  -d '{
    "doc_hashes": ["abc123..."],
    "collection": "kb_regulatory",
    "overwrite": false
  }'
```

**O que acontece:**
1. ✅ Busca chunks do `chunk_store`
2. ✅ Gera embeddings (OpenAI/local)
3. ✅ Cria points com ID determinístico: `{doc_hash}:{chunk_id}`
4. ✅ Upsert no Qdrant (idempotente)
5. ✅ Atualiza manifest: `vector_status=present`, `last_pushed_at=NOW()`

**Resultado:**
```json
{
  "pushed": 15,
  "skipped": 0,
  "collection": "kb_regulatory"
}
```

### 4. Verificar Status

Via UI:
```
http://localhost:8000/ui
→ Painel "✅ Documentos Aprovados"
→ Coluna "Vector" mostra badge verde "present"
```

## 🎨 Via Web UI

### Auto-Load ao abrir

A UI carrega automaticamente os últimos 100 aprovados ao abrir.

### Ações por Linha

**Rechunk:**
```
Clique "Rechunk" → POST /ingest/regenerate
Status: none → processing → done
```

**Push:**
```
Clique "Push" → POST /vector/push
Vector: none → present
```

**Remove:**
```
Clique "Remove" → POST /vector/delete
Vector: present → none
```

### Ações em Lote

1. ☑️ Selecione documentos (checkboxes)
2. 🎛️ Escolha ação: `Push to Vector`
3. ⚙️ Configure collection: `kb_regulatory`
4. ▶️ Clique "Executar seleção"
5. ✅ Status atualiza automaticamente (polling 5s)

## 🔍 Chunking Strategy (Implementado)

### PDF
```
1. Extract text by page (pdfplumber)
2. LLM markers from first 2-3 pages (Art., Cap., Anexo)
   → Prompt: "Sugira marcadores regex para segmentar este PDF regulatório"
3. Anchor-aware segmentation → Token chunks
   → Segments = split by markers
   → Chunks = max 512 tokens, overlap 50
4. Metadata: page_hint, anchor_type, segment_index
```

### HTML
```
1. Readability extraction (trafilatura)
2. Regex anchor detection (H1-H3, Art., Anexo, Tabela)
3. Anchor-aware (if 3+ anchors) → Token chunks
4. Fallback: token-only if few anchors
5. Metadata: source_type=html, num_anchors
```

### ZIP
```
(Not yet implemented - placeholder)
1. Extract nested files
2. Recursive processing for PDF/HTML
3. Table conversion for CSV/XLSX
```

## 🎯 Por que Anchors → Tokens?

✅ **Structure-first** - Preserva unidades semânticas (Art. 5º, Anexo II)  
✅ **Citation-friendly** - Chunks alinhados com estrutura regulatória  
✅ **Token-aware** - Max 512 tokens → custos previsíveis  
✅ **Overlap** - 50 tokens de sobreposição → melhor contexto  
✅ **Fallback robusto** - Sem anchors? Token chunking resolve  
✅ **Page-aware (PDF)** - LLM só nas primeiras páginas → otimização de custo

## 🧪 Testando

### 1. Iniciar Qdrant Local

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Testar Embeddings

```bash
python -c "
from embeddings.encoder import encode_texts
vecs = encode_texts(['teste'])
print(f'Dimension: {len(vecs[0])}')
"
```

### 3. Testar Push

```bash
# Via API
curl -X POST http://localhost:8000/vector/push \
  -H "Content-Type: application/json" \
  -d '{"doc_hashes":["abc123"], "collection":"test"}'

# Via UI
# 1. Abra http://localhost:8000/ui
# 2. Selecione documento
# 3. Clique "Push"
# 4. Monitore badge "Vector" → none → present
```

## 🔐 Idempotência

### Point ID Determinístico

```python
point_id = f"{doc_hash}:{chunk_id}"
```

**Benefícios:**
- ✅ Múltiplos pushes não duplicam
- ✅ Re-push atualiza embeddings/payload
- ✅ Overwrite opcional para limpar antes

### Overwrite vs. Upsert

**Sem overwrite (default):**
```
Push 1: Insere 10 chunks
Push 2: Atualiza os mesmos 10 chunks (upsert)
Resultado: 10 pontos no Qdrant
```

**Com overwrite:**
```
Push 1: Insere 10 chunks
Regenerate: Gera 15 chunks novos
Push 2 (overwrite=true): Deleta 10, insere 15
Resultado: 15 pontos no Qdrant
```

## 🚨 Troubleshooting

### Erro: "Collection not found"

**Causa:** Collection não existe no Qdrant

**Solução:** Automático! O código cria a collection automaticamente:
```python
ensure_collection(client, "kb_regulatory", dim=1536)
```

### Erro: "Dimension mismatch"

**Causa:** `EMBED_DIM` não bate com o modelo

**Solução:**
```bash
# Para text-embedding-3-small (1536)
EMBED_DIM=1536

# Para text-embedding-3-large (3072)
EMBED_DIM=3072
```

### Erro: "OpenAI API key not found"

**Causa:** `OPENAI_API_KEY` não configurado

**Solução:**
```bash
# Adicione ao .env
OPENAI_API_KEY=sk-proj-...
```

### Chunks não aparecem no Qdrant

**Debug:**
```bash
# 1. Verifique se chunks existem
curl "http://localhost:8000/chunks/status?doc_hashes=abc123"

# 2. Verifique logs do push
# Busque por: "push_start", "push_encode_failed", "push_upsert_failed"

# 3. Verifique Qdrant
curl "http://localhost:6333/collections/kb_regulatory"
```

## 📊 Monitoramento

### Via UI (Real-time)

Badges atualizam a cada 5s:
- **Cache:** `none` → `processing` → `done`
- **Vector:** `none` → `present`
- **Chunks:** Contador atualiza automaticamente

### Via API

```bash
# Status de manifests
curl "http://localhost:8000/chunks/status?doc_hashes=abc123,def456"

# Response
{
  "manifests": [
    {
      "doc_hash": "abc123",
      "status": "done",
      "chunk_count": 15,
      "vector_status": "present",
      "last_pushed_at": "2025-10-14T20:30:00Z",
      "last_pushed_collection": "kb_regulatory"
    }
  ]
}
```

## 🎓 Exemplos de Uso

### Fluxo Completo via CLI

```bash
# 1. Agentic Search (aprova documentos)
make agentic-html

# 2. Regenerar chunks dos aprovados
curl -X POST http://localhost:8000/ingest/regenerate \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.gov.br/ans/.../doc.pdf"],
    "overwrite": true
  }'

# 3. Push para VectorDB
curl -X POST http://localhost:8000/vector/push \
  -H "Content-Type: application/json" \
  -d '{
    "doc_hashes": ["abc123"],
    "collection": "kb_regulatory"
  }'

# 4. Verificar no Qdrant
curl "http://localhost:6333/collections/kb_regulatory/points/scroll" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "with_payload": true}'
```

### Fluxo Completo via UI

```
1. Abra: http://localhost:8000/ui
2. Digite prompt: "Buscar RNs ANS sobre prazos"
3. Clique "🧠 Gerar Plano"
4. Clique "🚀 Executar"
5. Aguarde aprovações (painel atualiza sozinho)
6. Vá em "✅ Documentos Aprovados"
7. Selecione todos (☑️)
8. Escolha "🔧 Rechunk (overwrite)"
9. Clique "▶️ Executar seleção"
10. Aguarde chunks (badge Cache: done)
11. Escolha "⬆️ Push to Vector"
12. Clique "▶️ Executar seleção"
13. Aguarde (badge Vector: present) ✅
14. PRONTO! Chunks no VectorDB com embeddings
```

## 🔬 Arquitetura Técnica

### Point ID Format

```
{doc_hash}:{chunk_id}
```

**Exemplo:**
```
abc123def456...:0
abc123def456...:1
abc123def456...:2
```

**Vantagens:**
- ✅ Determinístico
- ✅ Idempotente (múltiplos pushes não duplicam)
- ✅ Permite re-push parcial
- ✅ Facilita delete por doc_hash

### Payload Structure

```json
{
  "doc_hash": "abc123...",
  "chunk_id": "0",
  "chunk_index": 0,
  "source_type": "pdf",
  "url": "https://...",
  "title": "RN 259",
  "text_len": 1024,
  "tokens": 256,
  "anchor_type": "artigo",
  "anchor_text": "Art. 5º",
  "page_hint": 3,
  "pushed_at": "2025-10-14T20:30:00Z",
  "collection": "kb_regulatory"
}
```

### Embedding Generation

**OpenAI:**
```python
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["texto 1", "texto 2", ...]  # Batch support
)
embeddings = [item.embedding for item in response.data]
```

**Local (LM Studio/Ollama):**
```bash
# 1. Inicie LM Studio com modelo de embeddings
# 2. Configure:
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio  # qualquer valor
OPENAI_EMBEDDING_MODEL=nomic-embed-text  # ou outro
EMBED_DIM=768  # depende do modelo

# 3. API funciona igual (OpenAI-compatible)
```

## 📈 Performance

### Batch Processing

- Default: 64 chunks por batch
- Embeddings gerados em batch (OpenAI suporta até 2048 por request)
- Upsert em batch para Qdrant

**Estimativa:**
- 1000 chunks (512 tokens cada) ~ 512k tokens
- text-embedding-3-small: $0.02/1M tokens = **$0.01**
- Tempo: ~5-10s (depende da rede)

### Recomendações

**Para grandes volumes:**
```json
{
  "batch_size": 128,  // Aumentar para mais throughput
  "collection": "kb_regulatory"
}
```

**Para re-push completo:**
```json
{
  "overwrite": true,  // Limpa antes
  "batch_size": 64
}
```

## 🛡️ Robustez

### Error Handling

**Encode failure:**
```
→ Log: "push_encode_failed"
→ Per-doc status: "encode_error"
→ Skipped, não para o push dos outros docs
```

**Upsert failure:**
```
→ Log: "push_upsert_failed"
→ Per-doc status: "upsert_error"
→ Marca como "partial" se alguns batches ok
```

**Manifest update failure:**
```
→ Log: "push_manifest_update_failed"
→ Pontos JÁ estão no Qdrant
→ Manifest não atualizado (pode corrigir depois)
```

### Transações

- ❌ **Não** usa transação DB para push (operação externa)
- ✅ **Idempotente** via point_id determinístico
- ✅ **Rollback seguro** no regenerate (transação DB)
- ✅ **Retry manual** sempre possível (re-push)

## 🔗 Integração com Agentic Search

### Workflow Automático

```python
# No /ingest/regenerate com push_after=true
{
  "urls": ["https://..."],
  "overwrite": true,
  "push_after": true,  # ← Push automático após chunking
  "collection": "kb_regulatory"
}
```

**Resultado:**
1. ✅ Regenera chunks
2. ✅ Salva em chunk_store
3. ✅ Gera embeddings
4. ✅ Push para Qdrant
5. ✅ Manifest: `vector_status=present`

### Audit Trail

Toda operação logada:
- `push_start` - Início do push
- `push_batch_done` - Cada batch upsert
- `push_manifest_updated` - Manifest atualizado
- `push_done` - Conclusão com totais

**Busca nos logs:**
```bash
cat logs/api.log | grep "push_" | jq .
```

## 🎁 Recursos Adicionais

### Filtros no Qdrant

Buscar por doc_hash:
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

filter_condition = Filter(
    must=[
        FieldCondition(
            key="doc_hash",
            match=MatchValue(value="abc123...")
        )
    ]
)

points = client.scroll(
    collection_name="kb_regulatory",
    scroll_filter=filter_condition,
    limit=100
)
```

### Buscar por Tipo

```python
filter_condition = Filter(
    must=[
        FieldCondition(
            key="source_type",
            match=MatchValue(value="pdf")
        )
    ]
)
```

### Buscar por Anchor

```python
filter_condition = Filter(
    must=[
        FieldCondition(
            key="anchor_type",
            match=MatchValue(value="artigo")
        )
    ]
)
```

## 📚 Referências

- [Qdrant Docs](https://qdrant.tech/documentation/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [LM Studio](https://lmstudio.ai/)
- [Ollama](https://ollama.ai/)

---

**✅ Sistema Completo End-to-End:**

```
Agentic Search → Approve Docs → Regenerate Chunks → Push to Vector → Query RAG
```

**🎉 PRONTO PARA PRODUÇÃO! 🚀**

