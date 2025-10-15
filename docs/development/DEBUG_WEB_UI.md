<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 🐛 Debug Web UI - Guia Completo

## 🚀 **3 Formas de Debugar a UI**

### **1️⃣ Debug Automático (MELHOR!)**

```
1. Aperte F5
2. Escolha: "🌐 Web UI + API (Debug Server)"
3. Aguarde servidor iniciar
4. Browser ABRE AUTOMATICAMENTE em http://localhost:8000/ui
5. Use a UI normalmente
6. Backend está em debug - breakpoints funcionam!
```

**Breakpoints úteis:**
```python
# apps/api/main.py
linha 232: # Depois de plan_from_prompt()
linha 314: # Dentro de /agentic/run
linha 354: # Dentro de /agentic/iters

# pipelines/agentic_controller.py
linha 95:  # Início do loop
linha 220: # Depois de quality gates
linha 236: # Depois de LLM judge
```

**Como debugar:**
1. Coloque breakpoints nos arquivos acima
2. Na UI, clique "🧠 Gerar Plano"
3. VSCode PARA no breakpoint
4. Inspecione variáveis:
   - `plan.queries`
   - `plan.quality_gates`
5. F5 para continuar ou F10 passo-a-passo

---

### **2️⃣ Debug Manual (controle total)**

```
1. F5 → "🌐 UI Backend (Debug Endpoints)"
2. Servidor inicia (NÃO abre browser automaticamente)
3. Abra browser manualmente: http://localhost:8000/ui
4. Coloque breakpoints onde quiser
5. Use a UI, backend para nos breakpoints
```

**Quando usar:**
- Quer controlar quando abrir browser
- Quer múltiplas abas/testes
- Quer debugar fluxos específicos

---

### **3️⃣ Debug + Console Logs**

```
1. F5 → "🌐 Web UI + API (Debug Server)"
2. UI abre automaticamente
3. Aperte F12 no browser (DevTools)
4. Use Console + Network tabs
```

**No Console do Browser:**
```javascript
// Ver plan atual
document.getElementById('planJson')?.value

// Ver plan_id
currentPlanId

// Ver aprovados
approvedUrls

// Forçar refresh de iterations
buscarIters(currentPlanId)

// Debug de HTMX
htmx.logAll()
```

**Na aba Network:**
- Veja chamadas POST /agentic/plan
- Veja chamadas POST /agentic/run
- Veja polling GET /agentic/iters/{id}

---

## 🎯 **Cenários de Debug**

### **Cenário 1: LLM não retorna JSON válido**

**Problema:**
```
Erro ao processar plano: Unexpected token...
```

**Debug:**
```python
# Breakpoint em: agentic/llm.py linha 387
# Depois de response = self._call_chat_completion(...)

# Inspecione:
response  # String crua do LLM
plan_dict  # JSON parseado
```

**Solução:**
- Veja o `response` cru
- Ajuste system prompt se necessário
- LLM pode ter retornado texto em vez de JSON

---

### **Cenário 2: Nenhum candidato aprovado**

**Problema:**
```
Iter 1: aprovados: 0, rejeitados: 20
```

**Debug:**
```python
# Breakpoint em: pipelines/agentic_controller.py linha 220
# Depois de apply_quality_gates()

# Inspecione:
all_candidates  # Todos candidatos
filtered_candidates  # Depois de gates
rejected_this_iter  # Com violations
```

**Solução:**
- Veja `violations` - o que está rejeitando?
- Se `type:not_allowed`, relaxe `must_types`
- Se `score:low`, reduza `min_score`
- Se `age:stale`, aumente `max_age_years`

---

### **Cenário 3: Loop para antes do esperado**

**Problema:**
```
Stopped by: no_progress (esperava min_approved)
```

**Debug:**
```python
# Breakpoint em: pipelines/agentic_controller.py linha 280
# No if not approved_this_iter and not new_queries:

# Inspecione:
approved_this_iter  # Aprovados nesta iter
new_queries  # Novas queries do judge
judge_response  # Resposta completa do LLM
```

**Solução:**
- Judge não propôs novas queries
- E não aprovou nada
- Relaxe quality gates ou mude queries iniciais

---

### **Cenário 4: UI não carrega**

**Problema:**
```
404 Not Found - /ui
```

**Debug:**
```python
# Breakpoint em: apps/api/main.py linha 381
# Dentro de ui_console()

# Inspecione:
ui_file  # Caminho do arquivo
ui_file.exists()  # True ou False?
```

**Solução:**
- Verifique se `apps/ui/static/index.html` existe
- Caminho correto: `apps/ui/static/index.html`

---

## 🔬 **Breakpoints Estratégicos**

### **Para debug de planner:**
```python
# agentic/llm.py
linha 387:  # response do LLM (cru)
linha 398:  # plan construído e validado
```

### **Para debug de loop:**
```python
# pipelines/agentic_controller.py
linha 152:  # Depois de CSE query
linha 195:  # Depois de build candidate
linha 220:  # Depois de quality gates
linha 236:  # Depois de LLM judge
linha 280:  # Check stop conditions
```

### **Para debug de quality gates:**
```python
# agentic/quality.py
linha 27:  # Dentro do loop de gates
linha 50:  # Retorno (approved, violations)
```

### **Para debug de API endpoints:**
```python
# apps/api/main.py
linha 232:  # plan = llm.plan_from_prompt()
linha 314:  # result = run_agentic_search()
linha 354:  # iterations = AgenticIterDAO.get_iters()
```

---

## 📊 **Watch Variables Úteis**

Quando parar em breakpoint, adicione ao Watch:

```python
# No planner
plan.dict()
plan.queries
plan.quality_gates

# No loop
all_candidates[0].url
filtered_candidates
judge_response.approved_urls
judge_response.new_queries

# Nos gates
violations
candidate.final_type
candidate.score
candidate.anchor_signals
```

---

## 🎮 **Comandos de Debug VSCode**

| Tecla | Ação |
|-------|------|
| `F5` | Continue (próximo breakpoint) |
| `F10` | Step Over (próxima linha) |
| `F11` | Step Into (entrar na função) |
| `Shift+F11` | Step Out (sair da função) |
| `F9` | Toggle breakpoint |
| `Ctrl+Shift+F5` | Restart debug |
| `Shift+F5` | Stop debug |

---

## 💡 **Dicas Pro**

### **1. Debug Flow Completo:**

```
1. F5 → "🌐 Web UI + API (Debug Server)"
2. Breakpoint em: apps/api/main.py linha 314
3. Na UI, clique "🚀 Executar"
4. VSCode PARA no breakpoint
5. F11 para entrar em run_agentic_search()
6. F10 passo-a-passo pelo loop
7. Veja iterations em tempo real na UI!
```

### **2. Debug Só Backend:**

```
1. F5 → "🌐 UI Backend (Debug Endpoints)"
2. Breakpoints nos endpoints que quiser
3. Abra browser manualmente
4. Use UI normalmente
5. Backend para quando chamar endpoints
```

### **3. Debug Frontend (Browser):**

```
1. make ui
2. Abra browser: http://localhost:8000/ui
3. F12 (DevTools)
4. Tab "Console":
   - Veja erros JS
   - Digite comandos (ex: currentPlanId)
5. Tab "Network":
   - Veja requests HTTP
   - Clique para ver payload/response
```

---

## 🧪 **Teste Completo com Debug:**

```
Passo 1: Iniciar em debug
  F5 → "🌐 Web UI + API (Debug Server)"
  
Passo 2: Colocar breakpoints
  apps/api/main.py linha 232 (planner)
  apps/api/main.py linha 314 (loop)
  pipelines/agentic_controller.py linha 220 (quality gates)
  
Passo 3: Usar UI
  a) Digite prompt: "Buscar RNs ANS"
  b) Clique "🧠 Gerar Plano"
     → VSCode PARA no breakpoint linha 232
     → Inspecione: user_prompt, plan
     → F5 para continuar
  
  c) Clique "🚀 Executar"
     → VSCode PARA no breakpoint linha 314
     → Inspecione: plan, session, cse, llm
     → F11 para entrar em run_agentic_search()
     → VSCode PARA no breakpoint linha 220 (quality gates)
     → Inspecione: all_candidates, filtered_candidates, rejected_this_iter
     → F5 para continuar até fim
  
  d) Veja resultado na UI!
```

---

## 📝 **Logging na UI**

A UI usa **estrutlog** no backend. Para ver logs detalhados:

```bash
# Terminal onde rodou "make ui" mostra logs:
2025-10-14 19:10:00 [info] api_agentic_plan_start
2025-10-14 19:10:02 [info] llm_plan_done queries_count=3
2025-10-14 19:10:05 [info] api_agentic_run_start
2025-10-14 19:10:05 [info] agentic_search_start
2025-10-14 19:10:06 [info] agentic_iteration_start iteration=1
...
```

---

## 🎯 **Workflow Ideal:**

```
┌─ DESENVOLVIMENTO ─────────────────────────────────┐
│                                                    │
│  1. VSCode: F5 → "🌐 Web UI + API (Debug Server)" │
│     ↓                                              │
│  2. Browser abre automaticamente                  │
│     ↓                                              │
│  3. Use UI normalmente                            │
│     ↓                                              │
│  4. Backend para em breakpoints                   │
│     ↓                                              │
│  5. Inspecione variáveis                          │
│     ↓                                              │
│  6. F5 continua                                   │
│     ↓                                              │
│  7. Veja resultado na UI                          │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 🏆 **Configurações Disponíveis:**

| Config | Quando Usar |
|--------|-------------|
| 🌐 **Web UI + API (Debug Server)** | **RECOMENDADO!** Abre browser automaticamente |
| 🌐 **UI Backend (Debug Endpoints)** | Controle manual do browser |
| 🌐 **FastAPI Server** | Debug API sem UI |

---

## ⚡ **Quick Start:**

```
1. F5
2. Escolha: "🌐 Web UI + API (Debug Server)"
3. Browser abre sozinho em /ui
4. Use a UI!
```

**É só isso! Mais fácil impossível!** 🎉

---

**AGORA VOCÊ TEM DEBUG COMPLETO DA WEB UI NO VSCODE! 🔬🌐🚀**

