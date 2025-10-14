# 🚀 Agentic Search - Guia Rápido

## 🎯 O que é?

Sistema de busca autônoma com loop Plan→Act→Observe→Judge→Re-plan que:
- Gera plano de busca via LLM
- Executa queries iterativamente
- Aplica quality gates rigorosos
- Julga resultados semanticamente
- Refina queries automaticamente
- Para quando objetivo atingido

---

## ⚡ Uso Rápido

### **Modo 1: Prompt Direto (Mais Simples)**

```bash
python scripts/run_agentic.py --prompt "Buscar RNs da ANS sobre prazos de atendimento dos últimos 2 anos" --debug
```

**O que acontece:**
1. LLM gera plano automaticamente
2. Mostra o plano gerado
3. Executa loop agentivo
4. Salva tudo no DB
5. Mostra resultados

**Debug mode** (`--debug`):
- ✅ Output colorido no console
- ✅ Logs legíveis (não JSON)
- ✅ Perfeito para desenvolvimento

---

### **Modo 2: Gerar Plano → Editar → Executar**

```bash
# Passo 1: Gerar plano
python scripts/run_agentic.py \
  --prompt "Buscar RNs ANS sobre cobertura" \
  --plan-only \
  --output my_plan.json

# Passo 2: Editar my_plan.json (ajustar queries, gates, etc.)
nano my_plan.json

# Passo 3: Executar com plano editado
python scripts/run_agentic.py --plan-file my_plan.json --debug
```

**Quando editar:**
- Adicionar queries específicas
- Ajustar quality gates (ex: `min_score: 0.8`)
- Mudar stop conditions
- Adicionar domains no allowlist

---

### **Modo 3: Dry-Run (Simular sem DB)**

```bash
python scripts/run_agentic.py \
  --prompt "Buscar RNs ANS sobre prazos" \
  --dry-run
```

**O que faz:**
- ✅ Gera plano
- ✅ Mostra configuração
- ❌ NÃO executa queries reais
- ❌ NÃO salva no DB
- 👍 Perfeito para testar configuração

---

### **Modo 4: Via API (Produção)**

```bash
# Terminal 1: Iniciar API
make api

# Terminal 2: Criar plano
curl -X POST http://localhost:8000/agentic/plan \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Buscar RNs ANS sobre cobertura obrigatória 2024"}'

# Response: {"plan_id": "abc-123", "plan": {...}}

# Executar
curl -X POST http://localhost:8000/agentic/run \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "abc-123"}'

# Ver audit trail
curl http://localhost:8000/agentic/iters/abc-123
```

---

## 📊 Visualizar Audit Trail

```bash
# Via script (output colorido)
python scripts/view_agentic_iters.py <plan_id>

# JSON format
python scripts/view_agentic_iters.py <plan_id> --json

# Via API
curl http://localhost:8000/agentic/iters/<plan_id>
```

---

## 🔧 Configuração

### **Editar defaults** (`configs/agentic.yaml`):

```yaml
agentic:
  default_stop:
    min_approved: 12          # Meta de documentos
    max_iterations: 3         # Máximo de loops
    max_queries_per_iter: 2   # Queries por iteração
  
  default_quality:
    must_types: ["pdf", "zip"]  # Tipos permitidos
    max_age_years: 3            # Idade máxima
    min_anchor_signals: 1       # Mínimo de Art./Anexo
    min_score: 0.65             # Score mínimo
```

### **Quality Gates Explicados:**

| Gate | O que faz | Exemplo |
|------|-----------|---------|
| `must_types` | Só aceita esses tipos | `["pdf","zip"]` = só docs oficiais |
| `max_age_years` | Máximo de idade | `3` = nada antes de 2022 |
| `min_anchor_signals` | Marcadores estruturais | `1` = deve ter Art./Anexo/Tabela |
| `min_score` | Relevância mínima | `0.65` = 65% de match |

---

## 🧪 Exemplos de Prompts

### **Busca Específica:**
```
"Buscar a RN 395 da ANS e seus anexos sobre cobertura obrigatória"
```

### **Busca Abrangente:**
```
"Buscar todas as Resoluções Normativas da ANS sobre prazos máximos de atendimento publicadas entre 2020-2025, incluindo anexos e tabelas"
```

### **Busca com Restrições:**
```
"Buscar legislação do Planalto sobre proteção de dados pessoais na saúde (LGPD aplicada ao setor), apenas PDFs oficiais dos últimos 2 anos"
```

---

## 🐛 Debug & Troubleshooting

### **Ver logs detalhados:**
```bash
python scripts/run_agentic.py --prompt "..." --debug 2>&1 | tee agentic.log
```

### **Testar qualit gates isoladamente:**
```bash
pytest tests/test_agentic_quality.py -v -s
```

### **Verificar schemas:**
```bash
pytest tests/test_agentic_plan.py -v
```

### **Se falhar:**

1. **"Plan not found"** → Plan ID errado ou não existe no DB
2. **"CSE quota exceeded"** → Budget esgotado, aumente `max_cse_calls`
3. **"No progress"** → Queries não retornam resultados aprovados, relaxe quality gates
4. **JSON errors** → LLM retornou JSON inválido, reexecute (retry automático)

---

## 📈 Monitorar Progresso

Durante execução, você verá logs como:

```json
{"event": "agentic_search_start", "plan_id": "abc-123", "queries_count": 3}
{"event": "agentic_iteration_start", "iteration": 1}
{"event": "agentic_cse_query", "query": "RN ANS prazos"}
{"event": "agentic_cse_results", "count": 10}
{"event": "agentic_observe_done", "candidates_count": 8}
{"event": "agentic_quality_gates_applied", "passed": 5, "rejected": 3}
{"event": "llm_judge_start", "candidates_count": 5}
{"event": "llm_judge_done", "approved_count": 4, "rejected_count": 1, "new_queries_count": 2}
{"event": "agentic_iteration_complete", "total_approved": 4}
{"event": "agentic_iteration_start", "iteration": 2}
...
{"event": "agentic_stop_min_approved", "approved": 12}
```

---

## 💡 Dicas Pro

### **1. Teste com dry-run primeiro:**
```bash
python scripts/run_agentic.py --prompt "..." --dry-run
```

### **2. Salve plano para reusar:**
```bash
python scripts/run_agentic.py --prompt "..." --plan-only --output plan.json
# Edite plan.json
python scripts/run_agentic.py --plan-file plan.json
```

### **3. Ajuste gates para domínio:**
- **Saúde regulatória:** `must_types: ["pdf","zip"]`, `min_anchor_signals: 2`
- **Leis gerais:** `must_types: ["pdf"]`, `max_age_years: 10`
- **Exploratório:** `must_types: ["pdf","zip","html"]`, `min_score: 0.5`

### **4. Use allowlist restritivo:**
```json
"allow_domains": [
  "www.gov.br/ans",
  "www.planalto.gov.br",
  "www.in.gov.br"
]
```

---

## 📦 Instalação

```bash
# 1. Rodar migrações
make migrate
make migrate-agentic

# 2. Testar
pytest tests/test_agentic_*.py -v

# 3. Exemplo completo
python scripts/run_agentic.py \
  --plan-file examples/agentic_plan_example.json \
  --debug
```

---

## 🎓 Entendendo o Loop

```
ITERATION 1:
  Plan: ["RN ANS prazos", "RN cobertura"]
    ↓
  ACT: Executa 2 queries no Google CSE (10 hits cada)
    ↓
  OBSERVE: 20 candidatos → HEAD requests → type detect → score
    ↓
  HARD GATES: 20 candidatos → 12 passam (8 rejeitados: tipo HTML, score baixo)
    ↓
  LLM JUDGE: 12 candidatos → Aprova 8 (4 rejeitados: desatualizados)
             Propõe: ["RN 259 ANS anexos", "Tabela TUSS"]
    ↓
  SAVE: 8 aprovados no DB
  CHECK: 8 < 12 (min_approved) → Continue
    ↓
ITERATION 2:
  Re-plan: ["RN 259 ANS anexos", "Tabela TUSS"]
    ↓
  ACT: Executa 2 novas queries
    ↓
  ... (repete)
    ↓
  SAVE: Mais 5 aprovados
  CHECK: 13 ≥ 12 → STOP! ✅
    ↓
RESULT:
  13 documentos aprovados
  Todos PDF/ZIP oficiais, recentes, com anchors
  Promovidos para ingestão
```

---

## ✅ Próximos Passos

Depois de aprovar documentos:

```bash
# 1. Ingerir documentos aprovados
python pipelines/ingest_pipeline.py --limit 50

# 2. Gerar embeddings e carregar no Qdrant
python vector/qdrant_loader.py --input data/output/kb_regulatory.jsonl

# 3. Buscar no vectorDB
python pipelines/search_pipeline.py --query "prazos atendimento urgência"
```

---

**Sistema completo: BUSCA AGENTIVA → INGESTÃO INTELIGENTE → VECTOR DB!** 🚀

