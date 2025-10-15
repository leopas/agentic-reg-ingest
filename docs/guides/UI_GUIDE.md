<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 🌐 Agentic Search Console - Web UI Guide

## 🚀 **Como Usar**

### **1. Iniciar a UI:**

```bash
make ui
```

### **2. Abrir no browser:**

```
http://localhost:8000/ui
```

---

## 🎨 **Interface Visual**

### **Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  🤖 Agentic Search Console                                      │
│  Plan → Act → Observe → Judge → Re-plan | v2.0                  │
├────────────────────────────────┬────────────────────────────────┤
│  COLUNA ESQUERDA               │  COLUNA DIREITA                │
├────────────────────────────────┼────────────────────────────────┤
│  1️⃣ GERAR PLANO                │  3️⃣ ITERAÇÕES & AUDIT          │
│  ┌──────────────────────────┐  │  ┌──────────────────────────┐  │
│  │ [Textarea: Prompt]       │  │  │ Iter 1: ✅ 8 ✗ 5         │  │
│  │                          │  │  │ Queries: RN ANS...       │  │
│  └──────────────────────────┘  │  │ New: RN 259 anexos       │  │
│  [🧠 Gerar] [📋 Exemplo]       │  └──────────────────────────┘  │
│                                │  │ Iter 2: ✅ 5 ✗ 2         │  │
│  Plano JSON (editável):        │  └──────────────────────────┘  │
│  {...}                         │                                │
│                                ├────────────────────────────────┤
├────────────────────────────────┤  ✅ DOCUMENTOS APROVADOS       │
│  2️⃣ EXECUTAR LOOP              │  • rn-395.pdf [link]          │
│  [Plan ID: ______]             │  • rn-428.pdf [link]          │
│  [🚀 Executar] [⏸️ Pausar]     │  • rn-259.pdf [link]          │
│                                │  [💾 Baixar Lista (JSON)]     │
│  Resultado: 13 aprovados       │                                │
│  Stopped by: min_approved      │                                │
├────────────────────────────────┤                                │
│  ⚙️ CONFIGURAÇÃO AVANÇADA      │                                │
│  ☐ Usar LLM Local              │                                │
│                                │                                │
├────────────────────────────────┤                                │
│  ⚡ ATALHOS DE PIPELINE         │                                │
│  [🔍 Search] [📥 Ingest]       │                                │
│  Output: {...}                 │                                │
└────────────────────────────────┴────────────────────────────────┘
```

---

## 🎯 **Workflow na UI**

### **Cenário 1: Primeira vez (do zero)**

1. **Digite objetivo** na caixa de texto
   ```
   "Buscar RNs da ANS sobre prazos de atendimento dos últimos 2 anos"
   ```

2. **Clique "🧠 Gerar Plano"**
   - LLM processa (2-5s)
   - JSON aparece abaixo (editável!)

3. **Revise o plano** (opcional)
   - Ajuste `queries` se quiser queries específicas
   - Mude `quality_gates.min_score` se muito rigoroso
   - Adicione domains em `allow_domains`

4. **Clique "🚀 Executar"**
   - Loop começa
   - Iterações aparecem em tempo real (painel direita)
   - Auto-refresh a cada 3s

5. **Aguarde conclusão**
   - Quando parar (min_approved ou max_iterations)
   - Documentos aprovados aparecem na lista
   - Clique nos links para abrir PDFs

6. **Download lista** (opcional)
   - Clique "💾 Baixar Lista (JSON)"
   - Salva `approved_<plan_id>.json`

---

### **Cenário 2: Usar plan_id existente**

1. Cole plan_id no campo **"Plan ID"**
2. Clique **"🚀 Executar"**
3. Sistema carrega plano do DB e executa

---

### **Cenário 3: Testar pipelines rapidinho**

1. Clique **"🔍 Search Demo"**
   - Executa query demo no CSE
   - Mostra JSON de resposta

2. Clique **"📥 Ingest Demo"**
   - Processa 10 documentos
   - Mostra stats

---

## 🔧 **Edição de Planos**

### **No textarea JSON você pode editar:**

```json
{
  "queries": [
    {"q": "RN ANS prazos", "k": 10},
    {"q": "RN 395 ANS", "k": 5}  ← Adicione queries!
  ],
  "allow_domains": [
    "www.gov.br/ans",
    "www.planalto.gov.br"  ← Adicione domains!
  ],
  "quality_gates": {
    "must_types": ["pdf", "zip"],
    "min_score": 0.70,  ← Ajuste! Menor = mais permissivo
    "min_anchor_signals": 1
  },
  "stop": {
    "min_approved": 15  ← Meta maior
  }
}
```

**Depois de editar, clique "🚀 Executar"** - ele usa o JSON editado!

---

## 📊 **Interpretando Audit Trail**

### **Cada iteração mostra:**

```
┌─ ITERATION 1 ──────────
│ ✅ 8 ✗ 5               ← 8 aprovados, 5 rejeitados
│ Queries: RN ANS prazos, RN cobertura
│ New queries: RN 259 anexos
│ Summary: Iter 1: 8 approved, 5 rejected
│ Time: 2025-10-14 19:00:00
└─────────────────────────
```

**Badges:**
- 🟢 **Verde (✅)** - Aprovados por quality gates + LLM
- 🔴 **Vermelho (✗)** - Rejeitados (tipo errado, score baixo, etc.)

---

## ✅ **Lista de Aprovados**

### **Mostra:**
- Links clicáveis para cada PDF/ZIP
- Trunca nome do arquivo
- Hover mostra URL completo

### **Botão Download:**
- Exporta JSON com:
  ```json
  {
    "plan_id": "abc-123",
    "approved_count": 13,
    "urls": ["https://...", ...],
    "exported_at": "2025-10-14T19:05:00Z"
  }
  ```

---

## ⚙️ **Configuração Avançada (Toggle LLM Local)**

### **Para usar LM Studio ou Ollama:**

1. Marque **"☑ Usar LLM Local"**
2. Preencha:
   - **Base URL**: `http://localhost:1234/v1` (LM Studio)
   - **Modelo**: `llama-3.2-3b`
3. Execute normalmente

**⚠️ Nota:** Isso é **client-side config** (não salva no plano). Para usar LLM local em produção, configure no `.env`:
```bash
OPENAI_BASE_URL=http://localhost:1234/v1
```

---

## 🎨 **Design System**

### **Cores:**

| Elemento | Cor | Uso |
|----------|-----|-----|
| Background | `#0b0f14` | Fundo principal |
| Cards | `#0f1720` | Painéis |
| Borders | `#1f2937` | Divisórias |
| Primary | `#2563eb` | Botões principais |
| Success | `#22c55e` | Aprovados |
| Error | `#ef4444` | Rejeitados |
| Warning | `#f59e0b` | Avisos |
| Info | `#60a5fa` | Informação |
| Muted | `#94a3b8` | Texto secundário |

### **Tipografia:**
- **System UI** - Nativo do OS
- **Monospace** - Para JSON e URLs

---

## 🚀 **Atalhos de Teclado** (futuro)

Atualmente a UI não tem atalhos de teclado, mas você pode adicionar:

```javascript
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'Enter') {
    executarLoop();  // Ctrl+Enter = Executar
  }
});
```

---

## 📱 **Responsivo**

A UI é **responsiva**:
- **Desktop (>1024px)**: 2 colunas
- **Tablet/Mobile (<1024px)**: 1 coluna (stack vertical)

---

## 🔒 **Segurança**

✅ **Sem segredos no frontend** - Tudo server-side  
✅ **CORS não configurado** - Só localhost  
✅ **Sem autenticação** - Para uso interno/dev  

**Para produção, adicione:**
- Autenticação (OAuth2/JWT)
- CORS configurado
- Rate limiting
- HTTPS

---

## 🧪 **Testar UI**

```bash
# Smoke test
pytest tests/test_ui_smoke.py -v

# Manualmente
make ui
# Abra http://localhost:8000/ui
# Clique botões e veja se funciona
```

---

## 🎓 **Tecnologias Usadas**

| Tech | Versão | Link |
|------|--------|------|
| **HTMX** | 1.9.10 | Via CDN |
| **FastAPI** | 0.115+ | Backend |
| **Vanilla JS** | ES6+ | No build! |
| **CSS Grid** | Nativo | Layout |

**Zero build step! Zero npm! Zero webpack!** 🎉

---

## 💡 **Dicas Pro**

### **1. Auto-refresh iterations:**
- Quando executa, poll inicia automaticamente (3s)
- Clique "⏸️ Pausar Refresh" para parar
- Clique "🔄 Refresh" para atualizar manual

### **2. Editar plano antes de executar:**
- Gere plano
- Edite JSON no textarea
- **NÃO** preencha plan_id
- Clique "🚀 Executar" - usa JSON editado!

### **3. Reusar plan_id:**
- Se já tem um plan_id (de CLI ou API)
- Cole no campo "Plan ID"
- Clique executar - carrega do DB

### **4. Exportar aprovados:**
- Depois de completar
- Clique "💾 Baixar Lista"
- Use JSON para processar em batch

---

## 🐛 **Debug na UI**

### **Abrir DevTools (F12):**

1. **Console** - Veja erros JS
2. **Network** - Veja chamadas HTTP
3. **Elements** - Inspecione DOM

### **Logs comuns:**

```javascript
// Ver plan atual
console.log(document.getElementById('planJson').value)

// Ver plan_id
console.log(currentPlanId)

// Ver aprovados
console.log(approvedUrls)

// Forçar poll
buscarIters(currentPlanId)
```

---

## 🎬 **Demo Completo (Passo a Passo)**

```bash
# 1. Subir UI
make ui

# 2. Abrir browser
http://localhost:8000/ui

# 3. Na UI:
#    a) Digite: "Buscar RNs ANS prazos"
#    b) Clique "🧠 Gerar Plano"
#    c) Aguarde 3s (LLM processando)
#    d) Revise JSON (edite se quiser)
#    e) Clique "🚀 Executar"
#    f) Assista iterações em tempo real!
#    g) Quando completar, veja lista de aprovados
#    h) Clique "💾 Baixar Lista"

# 4. Profit! 🎉
```

---

## 📦 **Estrutura de Arquivos**

```
apps/ui/
├── __init__.py          # Módulo vazio
└── static/
    └── index.html       # UI completa (HTMX + CSS inline)

apps/api/main.py         # Serve /ui endpoint
```

**1 arquivo HTML = UI completa!** Sem build, sem npm, sem complicação! 🚀

---

**PRONTO PARA USAR! Basta `make ui` e abrir no browser!** 🎨✨

