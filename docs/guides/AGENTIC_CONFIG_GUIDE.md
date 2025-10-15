<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 🎛️ Agentic Search - Guia de Configuração

## 📍 **ONDE CONFIGURAR**

### **3 Lugares Principais:**

```
1. examples/agentic_plan_*.json  ← Planos prontos (edite antes de rodar)
2. configs/agentic.yaml          ← Defaults do sistema
3. No prompt (LLM gera pra você) ← Mais fácil!
```

---

## 🎯 **1. Allowlist (Quais domínios aceitar)**

### **Como funciona agora (CORRIGIDO!):**

```json
"allow_domains": [
  "www.gov.br/ans",        ← Aceita: www.gov.br/ans/* (qualquer path)
  "www.planalto.gov.br",   ← Aceita: todo planalto.gov.br
  "www.in.gov.br"          ← Aceita: todo in.gov.br
]
```

### **Exemplos:**

#### **Super Permissivo (aceita tudo .gov.br):**
```json
"allow_domains": ["gov.br"]
```

#### **Moderado (só órgãos específicos):**
```json
"allow_domains": [
  "www.gov.br/ans",
  "www.planalto.gov.br",
  "www.in.gov.br",
  "bvsms.saude.gov.br"
]
```

#### **Super Restrito (só DOU):**
```json
"allow_domains": [
  "www.in.gov.br/web/dou"
]
```

---

## 🚫 **2. Deny Patterns (O que BLOQUEAR)**

### **Regex patterns para rejeitar URLs:**

```json
"deny_patterns": [
  ".*\\/blog\\/.*",          // Bloqueia: /blog/
  ".*facebook.*",            // Bloqueia: facebook.com
  ".*twitter.*",             // Bloqueia: twitter.com
  ".*youtube\\.com.*"        // Bloqueia: youtube.com
]
```

### **⚠️ CUIDADO com estes:**

```json
// ❌ ERRADO - bloqueia DEMAIS
"deny_patterns": [".*noticia.*"]
// Isso bloqueia: /noticias/, /noticia/, /noticia-xyz/

// ✅ MELHOR - bloqueia só notícias individuais
"deny_patterns": [".*\\/noticia-.*", ".*\\/artigo-.*"]
// Isso bloqueia: /noticia-123/ mas permite /noticias/ (pasta)
```

### **Patterns Úteis:**

| Pattern | O que bloqueia |
|---------|----------------|
| `.*\\/blog\\/.*` | Qualquer /blog/ |
| `.*facebook.*` | Facebook |
| `.*linkedin.*` | LinkedIn |
| `.*wikipedia.*` | Wikipedia |
| `.*\\.pdf\\.html$` | Wrappers HTML de PDF |
| `.*download\\.php.*` | Scripts de download |

---

## ⚖️ **3. Quality Gates (Filtros de Qualidade)**

### **Tipos Permitidos:**

```json
"quality_gates": {
  "must_types": ["pdf", "zip"]    // Só documentos estruturados
}

// Outras opções:
"must_types": ["pdf"]              // SUPER restrito (só PDFs)
"must_types": ["pdf", "zip", "html"]  // Aceita HTML também
```

### **Idade Máxima:**

```json
"max_age_years": 3    // Nada antes de 2022

// Outros valores:
1  // Só último ano
5  // Últimos 5 anos
10 // Última década
0  // SEM filtro de idade (aceita qualquer)
```

### **Score Mínimo (Escala 0-5):**

```json
"min_score": 2.0    // Score mínimo (escala 0-5)

// Ajuste conforme necessidade:
1.5   // Muito permissivo (baixa qualidade OK)
2.0   // Balanceado (qualidade média)
2.5   // Rigoroso (boa qualidade)
3.0   // Muito rigoroso (alta qualidade)
3.5+  // Ultra rigoroso (apenas excelentes)
```

**Como o score funciona (soma ponderada 0-5):**
- Authority (0-1.0): Domínio .gov.br = 1.0
- Freshness (0-0.8): < 30 dias = 0.8
- Specificity (0-1.2): Keywords regulatórios
- Type boost (1.0-1.5): PDF=1.5, ZIP=1.3, HTML=1.0
- Anchorability (0-0.2): Art./Anexo/Tabela

**Exemplo de score alto (4.2):**
```
1.0 (gov.br) + 0.8 (recente) + 1.2 (RN no título) + 1.5 (PDF) + 0.2 (Art.) = 4.7
```

### **Anchor Signals (Marcadores Estruturais):**

```json
"min_anchor_signals": 1    // Deve ter pelo menos 1 Art./Anexo/Tabela

// Valores:
0  // SEM filtro de anchors
1  // Pelo menos 1 marcador
3  // Altamente estruturado (3+ marcadores)
```

**Marcadores detectados:**
- `Art. 123`, `Artigo 45`
- `ANEXO I`, `Anexo II`
- `Tabela 1`, `Tabela TUSS`
- `CAPÍTULO I`, `Capítulo II`
- `Seção III`, `Parágrafo 2`

---

## 🛑 **4. Stop Conditions (Quando parar)**

```json
"stop": {
  "min_approved": 12,           // Para quando tiver ≥12 aprovados
  "max_iterations": 3,          // Máximo 3 loops
  "max_queries_per_iter": 2     // 2 queries por vez
}
```

### **Ajuste conforme meta:**

| Meta | Config |
|------|--------|
| Rápido e leve | `min_approved: 5, max_iterations: 2` |
| Padrão | `min_approved: 12, max_iterations: 3` |
| Exaustivo | `min_approved: 50, max_iterations: 10` |

---

## 💰 **5. Budget (Controle de Custo)**

```json
"budget": {
  "max_cse_calls": 60,    // Máximo 60 chamadas ao Google CSE
  "ttl_days": 7           // Cache por 7 dias
}
```

**Cálculo aproximado:**
- 2 queries/iter × 3 iterations = 6 CSE calls
- Budget 60 = ~10 planos antes de atingir limite
- Google CSE free tier = 100 queries/dia

---

## 🎨 **TEMPLATES PRONTOS:**

### **Template: ANS (Permissivo)**
```bash
python scripts/run_agentic.py \
  --plan-file examples/agentic_plan_permissive.json \
  --debug
```

Aceita:
- ✅ PDFs e ZIPs da ANS
- ✅ Notícias oficiais (/noticias/)
- ✅ Arquivos diversos (/arquivos/)
- ✅ Últimos 3 anos
- ✅ Score ≥ 0.65

### **Template: DOU (Super Restrito)**
```bash
python scripts/run_agentic.py \
  --plan-file examples/agentic_plan_strict.json \
  --debug
```

Aceita:
- ✅ APENAS PDFs do Diário Oficial
- ✅ Score ≥ 0.85
- ✅ 3+ anchor signals
- ✅ Últimos 2 anos

---

## 🔧 **EDIÇÃO RÁPIDA:**

### **Ajustar allowlist rapidinho:**

```bash
# 1. Gerar plano
python scripts/run_agentic.py \
  --prompt "Buscar RNs ANS prazos" \
  --plan-only \
  --output temp.json

# 2. Editar allowlist
code temp.json

# Mude de:
"allow_domains": ["www.gov.br/ans"]

# Para (mais abrangente):
"allow_domains": ["gov.br"]

# 3. Rodar
python scripts/run_agentic.py --plan-file temp.json --debug
```

---

## 📊 **IMPACTO DAS CONFIGS:**

| Config | Muito Restrito | Balanceado | Permissivo |
|--------|----------------|------------|------------|
| **must_types** | `["pdf"]` | `["pdf","zip"]` | `["pdf","zip","html"]` |
| **min_score** | `0.85` | `0.70` | `0.50` |
| **max_age_years** | `1` | `3` | `5` |
| **min_anchor_signals** | `3` | `1` | `0` |
| **deny_patterns** | 20+ patterns | 5-10 patterns | 2-3 patterns |
| **Resultado** | Poucos e perfeitos | ~10-20 bons | 30+ variados |

---

## 🎯 **RECEITA PARA SEU CASO:**

Você quer **docs da ANS** (incluindo /noticias/ oficiais):

```json
{
  "allow_domains": [
    "www.gov.br/ans"        ← Agora funciona! ✅
  ],
  "deny_patterns": [
    ".*facebook.*",
    ".*twitter.*"
    // ❌ NÃO coloque ".*noticia.*" aqui!
  ],
  "quality_gates": {
    "must_types": ["pdf", "zip"],
    "max_age_years": 3,
    "min_anchor_signals": 1,
    "min_score": 0.65
  }
}
```

---

## 🚀 **RODE AGORA:**

```bash
# Use o plano permissivo (sem deny de noticias)
python scripts/run_agentic.py \
  --plan-file examples/agentic_plan_permissive.json \
  --debug
```

**Agora vai aceitar:**
- ✅ `www.gov.br/ans/pt-br/noticias/...`
- ✅ `www.gov.br/ans/pt-br/arquivos/...`
- ✅ `www.gov.br/ans/pt-br/centrais-de-conteudo/...`

**Enquanto rejeita:**
- ❌ Facebook, Twitter, etc.
- ❌ HTMLs (quality gate `must_types: ["pdf","zip"]`)
- ❌ Score < 0.65
- ❌ Documentos > 3 anos

---

**AGORA TÁ CONFIGURADO PERFEITO! 🎯✅**

