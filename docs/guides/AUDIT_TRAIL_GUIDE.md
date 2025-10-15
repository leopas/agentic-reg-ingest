<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 📊 Audit Trail - Guia de Interpretação

## 🎯 **O Que o Audit Trail Mostra**

Cada iteração do loop agentivo registra:
- ✅ **Aprovados** - URLs que passaram em TODOS os filtros
- ❌ **Rejeitados** - URLs que falharam + **motivos detalhados**
- 🔄 **Novas queries** - Queries propostas pelo LLM Judge
- 📝 **Queries executadas** - O que foi buscado no CSE

---

## 🌐 **Na Web UI**

### **Visual:**

```
┌─ ITERATION 1 ──────────────────
│ ✅ 8  ✗ 12
│ Queries: RN ANS prazos, RN cobertura
│ 🔄 Novas queries: RN 259 anexos
│
│ 🔍 Ver 12 rejeitados (com motivos) ▼
│   ❌ noticia-xyz/cancelamento
│   Razão: Tipo não permitido
│   Violations: type:not_allowed
│
│   ❌ blog-saude/artigo-123
│   Razão: Quality gates failed
│   Violations: type:not_allowed, score:low
│
│   ❌ rn-antiga.pdf
│   Razão: Documento desatualizado
│   Violations: age:stale (5.2 years > 3 years)
└─────────────────────────────────
```

**Como usar:**
1. Clique em **"🔍 Ver X rejeitados"** para expandir
2. Veja URL curta + razão + violations
3. Use para ajustar quality gates

---

## 💻 **No CLI**

### **Output:**

```bash
python scripts/view_agentic_iters.py <plan_id>

┌─ ITERATION 1 ─────────────────────────────────────────
│ Time: 2025-10-14T19:30:00
│
│ 📝 Executed Queries (2):
│   • RN ANS prazos máximos atendimento
│   • RN cobertura obrigatória
│
│ ✅ Approved (8):
│   ✓ rn-395.pdf
│     https://www.gov.br/ans/.../rn-395.pdf
│   ✓ rn-428.pdf
│     https://www.gov.br/ans/.../rn-428.pdf
│   ... and 6 more
│
│ ❌ Rejected (12) - COM MOTIVOS:
│   ✗ noticias/beneficiario/ans-tem-novas-regras
│     URL: https://www.gov.br/ans/pt-br/assuntos/noticias/...
│     💬 Razão: Quality gates failed
│     🚫 Violations: type:not_allowed (got 'html', want ['pdf', 'zip'])
│
│   ✗ documento-antigo.pdf
│     URL: https://example.com/documento-antigo.pdf
│     💬 Razão: Documento desatualizado
│     🚫 Violations: age:stale (5.2 years > 3 years)
│
│   ✗ blog/artigo-xyz
│     URL: https://blog.example.com/artigo-xyz
│     💬 Razão: Quality gates failed
│     🚫 Violations: score:low (1.2 < 2.0), anchors:insufficient (0 < 1)
│
│   ... and 9 more rejeitados
│
│ 🔄 New Queries Proposed (2):
│   → RN 259 ANS anexos
│   → Tabela TUSS procedimentos
│
│ 📌 Summary: Iter 1: 8 approved, 12 rejected
└───────────────────────────────────────────────────────
```

---

## 🔍 **Tipos de Violations**

### **1. Type Not Allowed**
```
type:not_allowed (got 'html', want ['pdf', 'zip'])
```

**Causa:** Documento não é do tipo permitido

**Solução:**
- Se quiser HTML, adicione em `must_types`: `["pdf", "zip", "html"]`
- Ou mantenha restrito (só docs oficiais)

---

### **2. Age Stale**
```
age:stale (5.2 years > 3 years)
```

**Causa:** Documento muito antigo

**Solução:**
- Aumente `max_age_years`: de `3` para `5` ou `10`
- Ou use `0` para sem limite de idade

---

### **3. Score Low**
```
score:low (1.2 < 2.0)
```

**Causa:** Score abaixo do threshold

**Solução:**
- Reduza `min_score`: de `2.0` para `1.5` ou `1.8`
- Scores típicos:
  - `1.0-1.5`: Baixa relevância
  - `2.0-2.5`: Relevância média
  - `3.0-3.5`: Alta relevância
  - `4.0+`: Excelente match

---

### **4. Anchors Insufficient**
```
anchors:insufficient (0 < 1)
```

**Causa:** Sem marcadores estruturais (Art., Anexo, Tabela)

**Solução:**
- Reduza `min_anchor_signals`: de `1` para `0`
- Ou aceite - pode ser wrapper HTML ou página sem estrutura

---

## 📈 **Analisar Padrões de Rejeição**

### **Se MUITOS rejeitados por type:**
```
12 rejeitados: type:not_allowed
```

**Ação:** Suas queries estão retornando HTML. Opções:
1. Adicione `filetype:pdf` nas queries
2. Ou relaxe: `"must_types": ["pdf", "zip", "html"]`

---

### **Se MUITOS rejeitados por score:**
```
15 rejeitados: score:low
```

**Ação:** Threshold muito alto. Opções:
1. Reduza `min_score` de `2.5` para `1.8`
2. Ou melhore queries (mais específicas)

---

### **Se MUITOS rejeitados por age:**
```
8 rejeitados: age:stale
```

**Ação:** Documentos antigos demais. Opções:
1. Aumente `max_age_years` de `2` para `5`
2. Ou busque content mais recente

---

## 💡 **Exemplos Reais**

### **Exemplo 1: Rejection Múltipla**
```
❌ https://blog.saude.com.br/artigo-123
   Razão: Quality gates failed
   Violations:
     • type:not_allowed (got 'html', want ['pdf', 'zip'])
     • score:low (1.1 < 2.0)
     • anchors:insufficient (0 < 1)
```

**Interpretação:** 
- É um blog (HTML)
- Score baixo (1.1)
- Sem marcadores estruturais
- **Veredicto:** Corretamente rejeitado! 👍

---

### **Exemplo 2: Rejection por Tipo**
```
❌ https://www.gov.br/ans/pt-br/noticias/operadora-x
   Razão: Tipo não permitido
   Violations: type:not_allowed (got 'html', want ['pdf', 'zip'])
```

**Interpretação:**
- É página HTML oficial (.gov.br)
- Mas você só quer PDFs/ZIPs
- **Veredicto:** Se quer notícias HTML, adicione `"html"` em `must_types`

---

### **Exemplo 3: Rejection por Idade**
```
❌ https://www.planalto.gov.br/ccivil/.../lei-antiga.htm
   Razão: Documento desatualizado
   Violations: age:stale (7.3 years > 3 years)
```

**Interpretação:**
- Lei de 2018 (7 anos atrás)
- Limite é 3 anos
- **Veredicto:** Se quer legislação histórica, aumente `max_age_years`

---

## 🎯 **Usar Violations para Ajustar Config**

### **Pipeline de Análise:**

```
1. Rode agentic search
2. Veja audit trail
3. Conte violations:
   - 15x type:not_allowed → Relaxe must_types
   - 20x score:low → Reduza min_score
   - 8x age:stale → Aumente max_age_years
4. Edite plano
5. Execute novamente
```

---

## 📊 **Estatísticas Úteis**

### **Na UI (após execução):**

Clique **"🔍 Ver X rejeitados"** em cada iteração para ver:
- Quais URLs foram rejeitadas
- Por que foram rejeitadas
- Quais violations específicas

### **No CLI (output completo):**

```bash
python scripts/view_agentic_iters.py <plan_id>

# Grep por violations:
python scripts/view_agentic_iters.py <plan_id> | grep "Violations:"

# Contar tipo de violation:
python scripts/view_agentic_iters.py <plan_id> --json | \
  jq '.iterations[].rejected[].violations[]' | \
  sort | uniq -c
```

---

## 🔬 **Debug: Por que foi rejeitado?**

### **Passo a Passo:**

1. **Veja no audit trail:**
   ```
   ❌ doc.pdf
   Razão: Quality gates failed
   Violations: score:low (1.8 < 2.0)
   ```

2. **Entenda o score:**
   - Score: `1.8`
   - Threshold: `2.0`
   - **Solução:** Reduza threshold para `1.5`

3. **Ajuste no plano:**
   ```json
   "quality_gates": {
     "min_score": 1.5  // Era 2.0, agora 1.5
   }
   ```

4. **Execute novamente**

---

## 📝 **Formato Completo de Rejected**

```json
{
  "url": "https://example.com/doc.pdf",
  "reason": "Quality gates failed",
  "violations": [
    "type:not_allowed (got 'html', want ['pdf', 'zip'])",
    "score:low (1.2 < 2.0)",
    "age:stale (5.2 years > 3 years)",
    "anchors:insufficient (0 < 1)"
  ]
}
```

**Campos:**
- `url` - URL completa
- `reason` - Descrição curta
- `violations` - Lista detalhada de problemas

---

## 🎓 **Entendendo o Sistema de Filtros**

```
Candidate CSE → Hard Quality Gates → Approved/Rejected
                   ↓ (se passed)
                LLM Judge → Approved/Rejected + New Queries
```

**Hard Gates (código):**
- ⚡ Rápido (ms)
- 🔒 Rigoroso (sem exceções)
- 📝 Violations explícitas

**LLM Judge (semântico):**
- 🧠 Inteligente (contexto)
- 🔄 Propõe queries
- 💬 Reasons em português

---

## 🏆 **Boas Práticas**

### **1. Comece permissivo, depois restrinja:**
```json
// Iteração 1: Permissivo
"min_score": 1.5,
"max_age_years": 5

// Se aprovou demais lixo:
"min_score": 2.5,
"max_age_years": 2
```

### **2. Use violations como guia:**
- Se 80% `type:not_allowed` → Queries erradas ou must_types
- Se 80% `score:low` → Threshold alto demais
- Se 80% `age:stale` → Limite de idade restrito

### **3. Itere o plano:**
```
Execução 1 → Ver violations → Ajustar gates → Execução 2
```

---

**AGORA O AUDIT TRAIL É COMPLETO E EXPLICA TUDO! 🔍📊✅**

**Recarregue a UI e veja as violations aparecerem!** 🚀

