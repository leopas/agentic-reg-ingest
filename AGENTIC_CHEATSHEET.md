# 🎯 Agentic Search - Cheat Sheet

## 🚀 Como Rodar (5 formas diferentes)

### **1️⃣ Modo Mais Simples (Windows)**
```cmd
run_agentic.bat "Buscar RNs da ANS sobre prazos de atendimento"
```

### **2️⃣ Modo Mais Simples (Linux/Mac)**
```bash
./scripts/run_agentic.sh "Buscar RNs da ANS sobre prazos de atendimento"
```

### **3️⃣ Com Make**
```bash
make agentic-example
```

### **4️⃣ CLI Direto**
```bash
python scripts/run_agentic.py --prompt "Buscar RNs ANS cobertura" --debug
```

### **5️⃣ Debug no VSCode**
Aperte `F5` → Escolha `🤖 Agentic Search (Debug)`

---

## 🐛 Debug no VSCode (RECOMENDADO!)

### **Configurações Disponíveis:**

| Nome | O que faz |
|------|-----------|
| 🤖 **Agentic Search (Debug)** | Roda com prompt, breakpoints funcionam! |
| 🤖 **Agentic Search (Example Plan)** | Usa plan exemplo, perfeito pra testar |
| 🤖 **Agentic Search (Dry-Run)** | Simula sem DB, ultra rápido |
| 🤖 **Agentic Search (Plan Only)** | Só gera plano, salva em JSON |
| 🔍 **Search Pipeline** | Pipeline de busca tradicional |
| 📥 **Ingest Pipeline** | Pipeline de ingestão |
| 🌐 **FastAPI Server** | API em modo debug |
| 🧪 **Run Current Test File** | Roda teste do arquivo aberto |
| 📊 **View Agentic Iterations** | Visualiza audit trail |

### **Como Usar:**

1. Aperte `F5` ou `Ctrl+Shift+D`
2. Escolha configuração no dropdown
3. Aperte `F5` de novo
4. **Coloque breakpoints** onde quiser debugar!

### **Breakpoints Úteis:**

```python
# agentic/llm.py
linha 385: # Depois de chamar LLM planner
linha 490: # Depois de chamar LLM judge

# pipelines/agentic_controller.py  
linha 150: # Depois de ACT (CSE query)
linha 180: # Depois de OBSERVE (metadata)
linha 200: # Depois de quality gates
linha 220: # Depois de JUDGE

# agentic/quality.py
linha 25:  # Validando cada gate
```

---

## 📋 Workflow Completo

### **Desenvolvimento:**
```bash
# 1. Gerar plano (debugar no VSCode)
F5 → "Agentic Search (Plan Only)"

# 2. Editar plano gerado
code my_generated_plan.json

# 3. Executar com plano editado (debugar)
# Edite launch.json temporariamente:
"args": ["--plan-file", "my_generated_plan.json", "--debug"]
F5 → "Agentic Search (Debug)"

# 4. Ver resultados
python scripts/view_agentic_iters.py <plan_id>
```

### **Produção (API):**
```bash
# 1. Subir API
make api

# 2. Criar plano
curl -X POST http://localhost:8000/agentic/plan \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Buscar RNs ANS prazos atendimento"}'

# 3. Executar
curl -X POST http://localhost:8000/agentic/run \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "..."}'

# 4. Ver iterations
curl http://localhost:8000/agentic/iters/...
```

---

## 🎨 Debug Output (--debug mode)

Com `--debug`, você vê logs **coloridos e legíveis**:

```
2025-10-14 18:30:15 [info     ] 🤖 Generating plan from prompt...
2025-10-14 18:30:17 [info     ] llm_plan_done          queries_count=3 min_approved=12
2025-10-14 18:30:17 [info     ] 🚀 Starting agentic search loop...
2025-10-14 18:30:18 [info     ] agentic_iteration_start iteration=1 plan_id=abc-123
2025-10-14 18:30:18 [info     ] agentic_cse_query      query=RN ANS prazos
2025-10-14 18:30:19 [info     ] agentic_cse_results    count=10
2025-10-14 18:30:22 [info     ] agentic_observe_done   candidates_count=8
2025-10-14 18:30:22 [info     ] agentic_quality_gates_applied passed=5 rejected=3
2025-10-14 18:30:23 [info     ] llm_judge_start        candidates_count=5
2025-10-14 18:30:25 [info     ] llm_judge_done         approved_count=4 rejected_count=1
2025-10-14 18:30:25 [info     ] agentic_iteration_complete total_approved=4
```

Sem `--debug`, vê JSON puro (produção):
```json
{"event": "agentic_iteration_start", "iteration": 1, "timestamp": "..."}
```

---

## 🔥 Comandos Rápidos

```bash
# Exemplo completo
make agentic-example

# Com seu prompt
python scripts/run_agentic.py --prompt "Buscar X" --debug

# Dry-run (sem DB)
python scripts/run_agentic.py --prompt "Buscar X" --dry-run

# Ver iterations
make agentic-view PLAN_ID=abc-123
# ou
python scripts/view_agentic_iters.py abc-123

# Ver como JSON
python scripts/view_agentic_iters.py abc-123 --json > audit.json
```

---

## 🛠️ Editar Plano Manualmente

```bash
# 1. Gerar
python scripts/run_agentic.py --prompt "..." --plan-only --output plan.json

# 2. Editar
code plan.json

# Ajuste o que quiser:
{
  "queries": [...],           # Adicione queries específicas
  "quality_gates": {
    "min_score": 0.8,         # Mais rigoroso
    "must_types": ["pdf"]     # Só PDFs
  },
  "stop": {
    "min_approved": 20        # Meta maior
  }
}

# 3. Executar
python scripts/run_agentic.py --plan-file plan.json --debug
```

---

## 🧪 Testar Componentes

```bash
# Quality gates
pytest tests/test_agentic_quality.py -v

# Schemas
pytest tests/test_agentic_plan.py -v

# Tudo
pytest tests/test_agentic_*.py -v
```

---

## 📊 Interpretar Resultados

### **Stop Reasons:**

| Stopped By | Significado | Ação |
|------------|-------------|------|
| `min_approved` | ✅ Meta atingida! | Success - prosseguir pra ingestion |
| `max_iterations` | ⚠️ Loop chegou no limite | Aumentar `max_iterations` ou relaxar gates |
| `budget` | 💰 Calls CSE esgotados | Aumentar `max_cse_calls` |
| `no_progress` | 🚫 Sem aprovações/queries | Relaxar quality gates ou mudar queries |

### **Violations Comuns:**

| Violation | Causa | Solução |
|-----------|-------|---------|
| `type:not_allowed` | HTML em vez de PDF/ZIP | Normal, é filtro funcionando |
| `age:stale` | Documento muito antigo | Aumentar `max_age_years` |
| `score:low` | Baixa relevância | Queries mais específicas |
| `anchors:insufficient` | Sem Art./Anexo/Tabela | Pode ser página wrapper |

---

## 💡 Exemplos de Prompts

### **Específico:**
```
"Buscar a RN 395 da ANS e todos os seus anexos"
```

### **Abrangente:**
```
"Buscar todas as RNs da ANS sobre rol de procedimentos publicadas entre 2020-2025"
```

### **Com Restrições:**
```
"Buscar legislação sobre LGPD na saúde, apenas PDFs oficiais do Planalto e ANPD, últimos 18 meses"
```

### **Tabelas:**
```
"Buscar tabela TUSS completa e atualizações, preferencialmente em formato ZIP ou PDF estruturado"
```

---

## 🎓 Variáveis de Ambiente

Certifique-se que `.env` tem:

```bash
OPENAI_API_KEY=sk-...
GOOGLE_CSE_API_KEY=...
GOOGLE_CSE_CX=...
MYSQL_HOST=...
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_DB=...
REQUEST_TIMEOUT_SECONDS=30  # ⚠️ ESPAÇO antes do # se tiver comentário!
```

---

## 🔗 Fluxo Completo

```bash
# 1. AGENTIC SEARCH (coletar docs de qualidade)
python scripts/run_agentic.py --prompt "..." --debug
# → Resultado: 15 PDFs/ZIPs aprovados no DB

# 2. INGESTÃO (processar docs)
python pipelines/ingest_pipeline.py --limit 50
# → Resultado: data/output/kb_regulatory.jsonl

# 3. VETORIZAÇÃO (embeddings + Qdrant)
python vector/qdrant_loader.py --input data/output/kb_regulatory.jsonl
# → Resultado: Chunks no Qdrant

# 4. BUSCA SEMÂNTICA
# (implementar query no vectorDB)
```

---

## ⚡ Shortcuts

| Comando | Atalho Windows | Atalho Linux/Mac |
|---------|----------------|------------------|
| Exemplo rápido | `run_agentic.bat --example` | `./scripts/run_agentic.sh --example` |
| Ver iterations | `run_agentic.bat --view PLAN_ID` | `./scripts/run_agentic.sh --view PLAN_ID` |
| Help | `run_agentic.bat --help` | `./scripts/run_agentic.sh --help` |

---

## 🏆 Dica Final

**Use VSCode Debug!** É disparado a melhor forma:
1. `F5` → Escolhe config
2. Coloca breakpoints
3. Vê variáveis em tempo real
4. Step-through no código

**Muito mais produtivo que logs!** 🚀

