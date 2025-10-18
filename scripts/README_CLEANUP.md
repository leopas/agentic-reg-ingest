# 🧹 Cleanup Scripts - Vision Enrichment

## 📄 Script: `cleanup_vision_enrichment.py`

Script seguro e completo para limpar dados da feature Vision Enrichment.

---

## 🎯 O Que Ele Limpa

### **Sempre:**
- ✅ Registros da tabela `vision_upload`

### **Opcionalmente:**
- 📁 Arquivos físicos (uploads, JSONL, TXTs)
- 📋 `agentic_plan` relacionados aos uploads
- 🔍 `search_results` relacionados aos uploads
- 📦 `chunk_manifest` com `source_pipeline='enrichment'`

---

## 🚀 Como Usar

### **1. Dry Run (Apenas Visualizar)**

```bash
python scripts/cleanup_vision_enrichment.py
```

Mostra o que seria deletado **SEM** deletar nada. **Sempre execute isso primeiro!**

---

### **2. Deletar Vision Upload + Arquivos**

```bash
python scripts/cleanup_vision_enrichment.py --execute
```

Deleta:
- ✗ Registros `vision_upload`
- ✗ Arquivos físicos (PDF, JSONL, TXTs)

**Mantém:**
- ✓ `agentic_plan`
- ✓ `search_results`
- ✓ `chunk_manifest`

---

### **3. Deletar TUDO**

```bash
python scripts/cleanup_vision_enrichment.py --execute --all
```

Deleta:
- ✗ Registros `vision_upload`
- ✗ Arquivos físicos
- ✗ `agentic_plan`
- ✗ `search_results`
- ✗ `chunk_manifest` (source_pipeline='enrichment')

**⚠️ Use com cautela!** Isso remove TODO o histórico de Agentic Search relacionado.

---

### **4. Deletar Apenas Registros (Manter Arquivos)**

```bash
python scripts/cleanup_vision_enrichment.py --execute --no-files
```

Útil se você quer:
- Reprocessar os mesmos arquivos do zero
- Manter backup dos arquivos originais

---

### **5. Deletar Apenas Agentic Data**

```bash
python scripts/cleanup_vision_enrichment.py --execute --agentic-data
```

Deleta:
- ✗ `vision_upload`
- ✗ Arquivos físicos
- ✗ `agentic_plan`
- ✗ `search_results`

**Mantém:**
- ✓ `chunk_manifest` (para não perder chunks já vectorizados)

---

## 🔒 Segurança

O script tem **múltiplas camadas de proteção**:

### **1. Dry Run por Padrão**
```bash
python scripts/cleanup_vision_enrichment.py
# ↑ NÃO deleta nada sem --execute
```

### **2. Confirmação Obrigatória**
```
Digite 'DELETAR' para confirmar:
```

Você deve digitar **exatamente** `DELETAR` (maiúsculas) para confirmar.

### **3. Preview Detalhado**
```
📄 AI-Canvas-Proposto-Auditoria-Regulatoria-via-RAG.pdf
   ID: 07da1342-7d0f-4f0f-97e8-0da9195c7edd
   Status: awaiting_review
   ✗ Arquivo: data\uploads\07da1342-...pdf
   ✗ JSONL: data\output\jsonl\07da1342-...jsonl
   ✗ TXT Dir: data\output\enrichment_txt\... (15 arquivos)
```

Mostra **exatamente** o que será deletado.

---

## 📊 Opções Disponíveis

| Opção | Descrição |
|-------|-----------|
| `--execute` | **Executar** a limpeza (sem isso = dry run) |
| `--no-files` | **Não** deletar arquivos físicos |
| `--agentic-data` | Deletar `agentic_plan` e `search_results` |
| `--chunks` | Deletar `chunk_manifest` (source_pipeline='enrichment') |
| `--all` | Deletar **TUDO** (= `--agentic-data --chunks`) |

---

## 🎯 Exemplos de Uso

### **Cenário 1: Testar Feature do Zero**

```bash
# 1. Ver o que tem
python scripts/cleanup_vision_enrichment.py

# 2. Limpar tudo
python scripts/cleanup_vision_enrichment.py --execute --all

# 3. Fazer novo upload
# Agora você tem um ambiente limpo!
```

---

### **Cenário 2: Reprocessar Com Novo GPT Hypothesis**

```bash
# 1. Deletar apenas registros (manter arquivos originais)
python scripts/cleanup_vision_enrichment.py --execute --no-files

# 2. Deletar JSONL cacheado manualmente
Remove-Item data\output\jsonl\*.jsonl

# 3. Fazer novo upload do mesmo arquivo
# O arquivo original ainda está em data\uploads\
# Mas será reprocessado do zero!
```

---

### **Cenário 3: Liberar Espaço (Manter Histórico)**

```bash
# Deletar apenas arquivos físicos (manter registros)
# Útil se você quer manter o histórico no banco
# mas liberar espaço em disco

# ⚠️ Não há opção direta para isso, mas você pode:
# 1. Fazer backup dos registros no banco
# 2. Deletar arquivos manualmente em data/uploads/, data/output/
```

---

## ⚠️ Avisos Importantes

### **1. Ação Irreversível**

```
⚠️  ATENÇÃO: ESTA AÇÃO NÃO PODE SER DESFEITA!
```

Faça **backup** se necessário antes de executar com `--execute`.

### **2. Cache de JSONL**

Se você deletar apenas registros (`--no-files`), o **cache de JSONL** será mantido.

Na próxima vez que processar o mesmo arquivo:
- ✅ OCR será pulado (cache hit)
- ✅ Gemini será pulado (cache hit)
- ✅ GPT Allowlist usará o JSONL cacheado

Para forçar reprocessamento completo:
```bash
# Deletar JSONL cacheado
Remove-Item data\output\jsonl\*.jsonl
```

### **3. Chunks no Qdrant**

O script **NÃO** deleta chunks do **Qdrant** (vector database).

Para deletar chunks do Qdrant, você precisa:
```python
# Exemplo (não implementado no script)
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# Deletar por filtro
client.delete(
    collection_name="kb_regulatory",
    points_selector={
        "filter": {
            "must": [
                {
                    "key": "meta.source_pipeline",
                    "match": {"value": "enrichment"}
                }
            ]
        }
    }
)
```

---

## 📝 Saída Exemplo

```
================================================================================
🧹 LIMPEZA: Vision Enrichment
================================================================================

📊 Uploads encontrados: 3

📄 AI-Canvas-Proposto-Auditoria-Regulatoria-via-RAG.pdf
   ID: 07da1342-7d0f-4f0f-97e8-0da9195c7edd
   Status: awaiting_review
   Criado: 2025-10-17 19:52:24
   ✗ Arquivo: data\uploads\07da1342-...pdf
   ✗ JSONL: data\output\jsonl\07da1342-...jsonl

📄 RAG-Production-Ready-Da-Viabilidade-ao-FinOps.pdf
   ID: 8a35ac60-8127-445e-864f-e60334c9b2f6
   Status: completed
   Criado: 2025-10-17 18:30:15
   ✗ Arquivo: data\uploads\8a35ac60-...pdf
   ✗ JSONL: data\output\jsonl\8a35ac60-...jsonl
   ✗ TXT Dir: data\output\enrichment_txt\8a35ac60-... (11 arquivos)

📋 Agentic Plans: 3
🔍 Search Results: 47

================================================================================
📊 RESUMO:
================================================================================
  Registros vision_upload: 3
  Arquivos físicos: 5
  Diretórios: 1
  Agentic plans: 3
  Search results: 47

⚠️  DRY RUN MODE - Nada será deletado
    Execute com --execute para aplicar as mudanças
```

---

## 🐛 Troubleshooting

### **Erro: "cannot import name 'AgenticPlan'"**

**Solução:** Já corrigido. O script usa apenas as models existentes.

### **Erro: "Session not found"**

**Solução:** Certifique-se de que está no diretório raiz do projeto:
```bash
cd C:\Projetos\agentic-reg-ingest
python scripts/cleanup_vision_enrichment.py
```

### **Erro: "Table not found"**

**Solução:** Execute as migrações primeiro:
```bash
mysql -u root -p agentic_reg < db\migrations\2025_10_17_vision_upload_table.sql
```

---

## ✅ Checklist Antes de Limpar

- [ ] Executei dry run primeiro
- [ ] Vi a lista completa do que será deletado
- [ ] Tenho backup (se necessário)
- [ ] Entendo que a ação é irreversível
- [ ] Tenho certeza das flags (--all, --no-files, etc.)

---

**Use com sabedoria!** 🧹✨

