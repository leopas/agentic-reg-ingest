<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 🧪 Testando o Sistema Agentic - Passo a Passo

## ✅ **Pré-requisitos**

Certifique-se que seu `.env` tem:

```bash
# ⚠️ IMPORTANTE: Usar MYSQL_DB (não MYSQL_DATABASE)
MYSQL_HOST=...
MYSQL_PORT=3306
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_DB=reg_cache              # ← Correto!

OPENAI_API_KEY=sk-...
GOOGLE_CSE_API_KEY=...
GOOGLE_CSE_CX=...

REQUEST_TIMEOUT_SECONDS=30      # ⚠️ Espaço antes do # se tiver comentário!
TTL_DAYS=7
```

---

## 🚀 **Teste Rápido (5 minutos)**

### **1. Dry-Run (sem API calls, sem DB)**
```bash
python scripts/run_agentic.py --prompt "Buscar RNs da ANS" --dry-run
```

**Esperado:**
```
🔮 DRY-RUN SIMULATION
========================================
Goal: Buscar RNs da ANS sobre...
Queries: 3
  1. RN ANS ... (k=10)
  2. ...
========================================
⚠️  Dry-run complete. Use without --dry-run to execute for real.
```

✅ Se funcionou, schemas e config estão OK!

---

### **2. Rodar com Example Plan (com API calls reais)**

**⚠️ Isso vai fazer chamadas reais ao Google CSE e OpenAI!**

```bash
# Via make
make agentic-example

# OU direto
python scripts/run_agentic.py \
  --plan-file examples/agentic_plan_example.json \
  --debug
```

**Esperado:**
```
2025-10-14 19:05:00 [info] 🚀 Starting agentic search loop...
2025-10-14 19:05:01 [info] agentic_iteration_start iteration=1
2025-10-14 19:05:02 [info] agentic_cse_query query=RN ANS prazos
2025-10-14 19:05:03 [info] agentic_cse_results count=10
...
========================================
🎉 AGENTIC SEARCH COMPLETE
========================================
Plan ID: abc-123-456
Iterations: 2
Approved total: X
...
```

✅ Se chegou até aqui, **TUDO funcionou**!

---

### **3. Ver Audit Trail**

```bash
# Pegar plan_id do output anterior
python scripts/view_agentic_iters.py <plan_id>
```

**Esperado:**
```
┌─ ITERATION 1 ─────────────
│ 📝 Executed Queries (2):
│   • RN ANS prazos
│   • RN cobertura
│
│ ✅ Approved (8):
│   ✓ https://www.gov.br/ans/.../rn-395.pdf
│   ...
│
│ ❌ Rejected (5):
│   ✗ https://.../noticia-xyz
│     Reason: Tipo não permitido
│     Violations: type:not_allowed
└─────────────────────────────
```

---

## 🐛 **Debug no VSCode (MELHOR OPÇÃO)**

### **Setup:**
1. Abra VSCode
2. Vá em "Run and Debug" (`Ctrl+Shift+D`)
3. Escolha **`🤖 Agentic Search (Debug)`** no dropdown
4. Aperte `F5`

### **Coloque Breakpoints:**

**Pontos estratégicos:**

```python
# agentic/llm.py
linha 398:  # Depois de criar Plan
linha 517:  # Depois de Judge Response

# pipelines/agentic_controller.py
linha 95:   # Início do loop
linha 152:  # Depois de CSE query
linha 195:  # Depois de build candidate
linha 220:  # Depois de quality gates
linha 236:  # Depois de LLM judge
linha 280:  # Check stop conditions

# agentic/quality.py
linha 27:   # Cada quality gate
```

### **Variáveis para Inspecionar:**

No breakpoint, veja:
- `plan.queries` - Queries planejadas
- `candidates` - Candidatos coletados
- `filtered_candidates` - Após quality gates
- `judge_response.approved_urls` - Aprovados pelo LLM
- `all_approved_urls` - Total acumulado

---

## 🧪 **Rodar Testes**

```bash
# Schemas
pytest tests/test_agentic_plan.py -v

# Quality gates
pytest tests/test_agentic_quality.py -v

# Tudo agentic
pytest tests/test_agentic_*.py -v
```

**Esperado:**
```
tests/test_agentic_plan.py::TestPlanSchema::test_minimal_plan PASSED
tests/test_agentic_plan.py::TestPlanSchema::test_full_plan PASSED
...
tests/test_agentic_quality.py::TestApplyQualityGates::test_all_gates_pass PASSED
...
=================== X passed in Y.YYs ===================
```

---

## 🔧 **Troubleshooting**

### **Erro: "MYSQL_DATABASE Field required"**
✅ **CORRIGIDO!** Use `MYSQL_DB` no `.env` (não `MYSQL_DATABASE`)

```bash
# .env (CORRETO)
MYSQL_DB=reg_cache

# .env (ERRADO - não use!)
MYSQL_DATABASE=reg_cache
```

### **Erro: "Timeout value connect was X#..."**
✅ **CORRIGIDO!** Adicione espaço antes do `#`:

```bash
# ERRADO
REQUEST_TIMEOUT_SECONDS=30# comentário

# CERTO
REQUEST_TIMEOUT_SECONDS=30  # comentário
```

### **Erro: "Plan not found"**
- Plan ID está errado
- Ou rode com `--plan-file` em vez de `--plan-id`

### **Erro: "CSE quota exceeded"**
- Você excedeu quota do Google CSE
- Reduza `max_cse_calls` no plano
- Ou espere reset da quota

### **Erro: JSON parse error (LLM)**
- LLM retornou JSON inválido (raro)
- Sistema faz retry automático (3x)
- Se persistir, veja logs: `llm_plan_json_error` ou `llm_judge_json_error`

---

## 📊 **Validar Componentes Isolados**

### **1. Testar Settings:**
```python
python -c "from common.settings import settings; print(settings.mysql_db)"
# Deve imprimir: reg_cache (ou seu DB)
```

### **2. Testar DB Connection:**
```python
python -c "from db.session import DatabaseSession; db=DatabaseSession(); print('OK')"
# Deve imprimir: OK
```

### **3. Testar LLM Client:**
```python
python -c "from agentic.llm import LLMClient; from common.settings import settings; llm=LLMClient(settings.openai_api_key); print('OK')"
# Deve imprimir: OK
```

### **4. Testar CSE Client:**
```python
python -c "from agentic.cse_client import CSEClient; from common.env_readers import load_yaml_with_env; cfg=load_yaml_with_env('configs/cse.yaml'); cse=CSEClient(cfg['api_key'], cfg['cx'], 30); print('OK')"
# Deve imprimir: OK
```

---

## 🎯 **Testes por Nível**

### **Level 1: Unit Tests (sem API calls)**
```bash
pytest tests/test_agentic_plan.py -v      # Schemas
pytest tests/test_agentic_quality.py -v   # Quality gates
pytest tests/test_env_readers.py -v       # Config loading
```

### **Level 2: Integration (mock APIs)**
```bash
pytest tests/test_router_llm.py -v        # Router (com mocks)
pytest tests/test_html_extractor.py -v    # HTML extract (sem LLM)
```

### **Level 3: End-to-End (API calls reais)**
```bash
# Dry-run
python scripts/run_agentic.py --prompt "Test" --dry-run

# Real (cuidado com quotas!)
python scripts/run_agentic.py \
  --plan-file examples/agentic_plan_example.json \
  --debug
```

---

## 🎨 **VSCode Debug - Cenários**

### **Cenário 1: Debugar Planner**
```
1. Abra: agentic/llm.py
2. Breakpoint: linha 398 (depois de criar Plan)
3. F5 → "🤖 Agentic Search (Plan Only)"
4. Inspecione: plan.queries, plan.quality_gates
```

### **Cenário 2: Debugar Loop Completo**
```
1. Abra: pipelines/agentic_controller.py
2. Breakpoints:
   - linha 152 (depois de CSE)
   - linha 220 (depois de quality gates)
   - linha 236 (depois de judge)
3. F5 → "🤖 Agentic Search (Example Plan)"
4. F10 para passo-a-passo
```

### **Cenário 3: Debugar Quality Gates**
```
1. Abra: agentic/quality.py
2. Breakpoint: linha 27 (loop de validação)
3. F5 → "🤖 Agentic Search (Example Plan)"
4. Inspecione: violations array
```

---

## 📋 **Checklist de Sucesso**

- [ ] Dry-run completa sem erros
- [ ] Testes unitários passam
- [ ] Plan gerado via prompt tem queries válidas
- [ ] Loop executa pelo menos 1 iteração
- [ ] Quality gates rejeitam candidatos ruins
- [ ] LLM judge retorna JSON válido
- [ ] Iterations salvam no DB
- [ ] Viewer mostra audit trail
- [ ] API endpoints respondem

**Se todos ✅, sistema está 100% operacional!** 🎉

---

## 💡 **Dica de Ouro**

**Use SEMPRE o debug mode no desenvolvimento:**

```bash
python scripts/run_agentic.py --prompt "..." --debug
```

**Não use JSON logs na hora de desenvolver!** Eles são pra produção.

**Atalho no VSCode: `F5` é seu melhor amigo!** 🚀

