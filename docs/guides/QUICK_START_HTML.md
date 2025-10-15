<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# ⚡ Quick Start - Buscar HTMLs

## 🎯 **Seu Caso: Precisa de HTMLs**

Você quer buscar **páginas HTML** (não PDFs), então use o plano específico!

---

## 🚀 **3 Formas de Rodar (HTML Only):**

### **1️⃣ Make (Mais Fácil)**
```bash
make agentic-html
```

### **2️⃣ Wrapper Windows**
```cmd
run_agentic.bat --html
```

### **3️⃣ Wrapper Linux/Mac**
```bash
./scripts/run_agentic.sh --html
```

### **4️⃣ VSCode Debug**
```
F5 → "🤖 Agentic Search (HTML Only)"
```

---

## ✅ **O Que Este Plano Faz:**

```json
{
  "goal": "Buscar páginas HTML sobre falhas de TI na saúde",
  "queries": [
    "falhas tecnologia informação saúde suplementar",
    "dívidas técnicas saúde suplementar custos",
    "ineficiências TI operadoras planos saúde"
  ],
  "quality_gates": {
    "must_types": ["html"],          ← SÓ HTML!
    "max_age_years": 5,              ← Aceita até 5 anos
    "min_anchor_signals": 0,         ← Sem exigência de Art./Anexo
    "min_score": 1.5                 ← Threshold baixo (HTML tem score menor)
  }
}
```

**Resultado esperado:**
- ✅ Aprova páginas HTML da ANS
- ✅ Aprova notícias oficiais
- ✅ Aprova páginas informativas
- ❌ Rejeita PDFs (só quer HTML)
- ❌ Rejeita muito antigos (>5 anos)

---

## 📊 **Comparação de Planos:**

| Plano | must_types | min_score | Quando usar |
|-------|------------|-----------|-------------|
| `agentic_plan_example.json` | `["pdf","zip"]` | `2.0` | Docs oficiais estruturados |
| `agentic_plan_permissive.json` | `["pdf","zip"]` | `1.8` | PDFs com threshold menor |
| `agentic_plan_html_only.json` | `["html"]` | `1.5` | **⭐ SEU CASO! Páginas web** |
| `agentic_plan_strict.json` | `["pdf"]` | `3.5` | Só PDFs excelentes |

---

## 🔧 **Editar Plano HTML:**

**Arquivo:** `examples/agentic_plan_html_only.json`

```json
{
  "queries": [
    {
      "q": "falhas TI saúde suplementar",
      "why": "Identificar problemas de TI",      ← Agora preenche!
      "k": 10
    }
  ],
  "quality_gates": {
    "must_types": ["html"],              ← Só HTML
    "min_anchor_signals": 0,             ← 0 = sem exigência de anchors
    "min_score": 1.5                     ← Baixo = mais permissivo
  }
}
```

**Ajuste conforme necessário:**
- Mais rigoroso: `min_score: 2.0`
- Aceitar também PDFs: `must_types: ["html", "pdf"]`
- Só últimos 2 anos: `max_age_years: 2`

---

## 🎯 **RODE AGORA:**

```bash
# Opção 1: Make
make agentic-html

# Opção 2: Wrapper
run_agentic.bat --html

# Opção 3: Direto
python scripts/run_agentic.py \
  --plan-file examples/agentic_plan_html_only.json \
  --debug
```

**Resultado esperado:**
```
Iter 1: 10 approved (HTMLs!) ✅
Iter 2: 5 approved
STOP: min_approved (15 ≥ 10)

Approved URLs:
  • https://www.gov.br/ans/.../falhas-ti
  • https://www.gov.br/ans/.../dividas-tecnicas
  ...
```

---

## 💡 **Dica: Via Web UI**

1. **Abra:** http://localhost:8000/ui
2. **Digite prompt:**
   ```
   Buscar sobre falhas de TI na saúde suplementar, ACEITAR APENAS PÁGINAS HTML
   ```
3. **Clique "🧠 Gerar Plano"**
4. **LLM vai gerar com `must_types: ["html"]`** automaticamente!
5. **Ou edite manualmente** o JSON antes de executar

---

## 🎓 **Por Que HTMLs Precisam de Config Diferente:**

| Aspecto | PDFs | HTMLs |
|---------|------|-------|
| **Anchors** | Geralmente tem (Art., Anexo) | Raramente tem |
| **Score** | Mais alto (1.5 boost) | Mais baixo (1.0 boost) |
| **Estrutura** | Sempre estruturado | Varia muito |
| **min_anchor_signals** | `1-3` | `0` |
| **min_score** | `2.0-3.0` | `1.5-2.0` |

---

## ✅ **MUDANÇAS APLICADAS:**

1. ✅ Schema `why` agora tem **default** ("Query relevante ao objetivo")
2. ✅ LLM **instruído a preencher** `why` sempre
3. ✅ Criado **plano específico para HTML** (`agentic_plan_html_only.json`)
4. ✅ Adicionado **comando `make agentic-html`**
5. ✅ Adicionado **`--html` nos wrappers**
6. ✅ Adicionado **debug config no VSCode**

---

## 🚀 **TESTE AGORA:**

```bash
make agentic-html
```

**Ou:**
```bash
run_agentic.bat --html
```

**Agora vai aprovar HTMLs! 🎉📄✅**
