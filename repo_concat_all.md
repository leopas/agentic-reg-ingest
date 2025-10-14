# Repository Snapshot (All text files)
- Root: `C:\Projetos\agentic-reg-ingest`
- Generated at: 2025-10-14 16:50:29
- Git commit: (n/a)
- Files included: 54 (max 2000000 bytes per file, text-only heuristic)

## [1] .env.example

```
// FILE: .env.example
// FULL: C:\Projetos\agentic-reg-ingest\.env.example
// NOTE: Concatenated snapshot for review
﻿# Google Programmable Search Engine (CSE)
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_CX=your-custom-search-engine-id-here

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# MySQL Database (Azure Database for MySQL compatible)
MYSQL_HOST=host.mysql.database.azure.com
MYSQL_PORT=3306
MYSQL_DB=reg_cache
MYSQL_USER=user@host
MYSQL_PASSWORD=super-secret-password

# SSL Configuration
# For production with SSL verification, provide full path to CA certificate:
# MYSQL_SSL_CA=C:\path\to\DigiCertGlobalRootCA.crt.pem
# For development without SSL verification, leave empty:
MYSQL_SSL_CA=

# Application Settings
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=30
TTL_DAYS=7

# Vector Database (Qdrant - optional)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=kb_regulatory

```

## [2] AGENTIC_CHEATSHEET.md

````markdown
# FILE: AGENTIC_CHEATSHEET.md
# FULL: C:\Projetos\agentic-reg-ingest\AGENTIC_CHEATSHEET.md
# NOTE: Concatenated snapshot for review
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


````

## [3] AGENTIC_CONFIG_GUIDE.md

````markdown
# FILE: AGENTIC_CONFIG_GUIDE.md
# FULL: C:\Projetos\agentic-reg-ingest\AGENTIC_CONFIG_GUIDE.md
# NOTE: Concatenated snapshot for review
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


````

## [4] AGENTIC_QUICKSTART.md

````markdown
# FILE: AGENTIC_QUICKSTART.md
# FULL: C:\Projetos\agentic-reg-ingest\AGENTIC_QUICKSTART.md
# NOTE: Concatenated snapshot for review
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


````

## [5] AUDIT_TRAIL_GUIDE.md

````markdown
# FILE: AUDIT_TRAIL_GUIDE.md
# FULL: C:\Projetos\agentic-reg-ingest\AUDIT_TRAIL_GUIDE.md
# NOTE: Concatenated snapshot for review
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


````

## [6] CHANGELOG.md

```markdown
# FILE: CHANGELOG.md
# FULL: C:\Projetos\agentic-reg-ingest\CHANGELOG.md
# NOTE: Concatenated snapshot for review
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-14

### Added
- Initial release
- Search pipeline with Google Custom Search Engine integration
- Multi-factor scoring system (authority, freshness, specificity, type, anchorability)
- MySQL caching with configurable TTL
- Ingest pipeline with diff detection
- LLM-powered document routing (PDF/ZIP/HTML)
- PDF processing with intelligent chunking using LLM-suggested anchors
- ZIP archive processing with table detection
- HTML content extraction and processing
- Token-aware chunking with configurable overlap
- JSONL output for knowledge base
- Qdrant vector database integration
- FastAPI REST API with health checks
- Structured logging with trace IDs
- Docker support with docker-compose
- Comprehensive test suite
- Makefile for common tasks
- Documentation and examples

### Configuration
- Environment-based configuration via `.env`
- YAML configs with variable interpolation
- Secure credential management (no hardcoded secrets)

### Infrastructure
- SQLAlchemy 2.x with MySQL support
- Azure Database for MySQL compatible
- Pydantic settings management
- Tenacity for retry logic
- Structlog for JSON logging

### Quality
- Black code formatting
- Ruff linting
- MyPy type checking
- Pytest test framework
- 95%+ test coverage for core modules

[1.0.0]: https://github.com/your-org/agentic-reg-ingest/releases/tag/v1.0.0


```

## [7] CHANGELOG_AGENTIC.md

````markdown
# FILE: CHANGELOG_AGENTIC.md
# FULL: C:\Projetos\agentic-reg-ingest\CHANGELOG_AGENTIC.md
# NOTE: Concatenated snapshot for review
# 📝 Changelog - Agentic Search Implementation

## [2.0.0] - 2025-10-14 - AGENTIC SEARCH RELEASE 🚀

### 🎉 **MEGA FEATURE: True Agentic Search**

Transformação completa do sistema de busca linear para **loop agentivo autônomo** com Plan→Act→Observe→Judge→Re-plan.

---

## ✨ **Added**

### **Agentic Search System**
- **LLM Planner** (`agentic/llm.py::plan_from_prompt()`) - Gera plano estruturado via prompt
- **LLM Judge** (`agentic/llm.py::judge_candidates()`) - Avalia candidatos semanticamente
- **Agentic Controller** (`pipelines/agentic_controller.py`) - Loop completo (550 linhas)
- **Pydantic Schemas** (`agentic/schemas.py`) - Models validados: Plan, Judge, Quality
- **Quality Gates** (`agentic/quality.py`) - Filtros multi-critério + anchor detection
- **Audit Tables** - `agentic_plan` e `agentic_iter` para compliance

### **CLI & Debug Tools**
- **CLI Runner** (`scripts/run_agentic.py`) - Interface completa com dry-run e debug mode
- **Iteration Viewer** (`scripts/view_agentic_iters.py`) - Visualizador de audit trail
- **VSCode Launch Config** (`.vscode/launch.json`) - 12 configurações de debug
- **Windows Wrapper** (`run_agentic.bat`) - Atalho simples
- **Linux/Mac Wrapper** (`scripts/run_agentic.sh`) - Atalho simples

### **API Endpoints**
- `POST /agentic/plan` - Criar plano via prompt
- `POST /agentic/run` - Executar loop agentivo
- `GET /agentic/iters/{plan_id}` - Ver audit trail

### **Configuration**
- **Agentic Config** (`configs/agentic.yaml`) - Defaults para stop/quality/budget
- **Example Plan** (`examples/agentic_plan_example.json`) - Plano pronto para usar

### **Documentation**
- **Quickstart Guide** (`AGENTIC_QUICKSTART.md`) - Tutorial completo
- **Cheat Sheet** (`AGENTIC_CHEATSHEET.md`) - Referência rápida
- **Test Guide** (`TEST_AGENTIC.md`) - Como testar e debugar
- **README Section** - Seção "Agentic Search" detalhada

### **Tests**
- `tests/test_agentic_plan.py` - Schema validation (8 tests)
- `tests/test_agentic_quality.py` - Quality gates (8 tests)

### **Makefile Targets**
- `make migrate-agentic` - Rodar migração agentic
- `make agentic-example` - Executar com plano exemplo
- `make agentic-view PLAN_ID=...` - Ver iterations

---

## 🔧 **Changed**

### **LLM Module**
- Extended `agentic/llm.py` with planner and judge methods (+210 lines)

### **Database**
- Extended `db/dao.py` with `AgenticPlanDAO` and `AgenticIterDAO` (+135 lines)
- Added `agentic_plan` and `agentic_iter` tables (migration)

### **API**
- Extended `apps/api/main.py` with 3 agentic endpoints (+185 lines)
- Added request/response models for agentic endpoints

### **Documentation**
- Updated `README.md` with comprehensive Agentic Search section (+230 lines)
- Updated `Makefile` help text

---

## 🐛 **Fixed**

### **Settings & Environment**
- Fixed `common/settings.py` to use `mysql_db` instead of `MYSQL_DATABASE`
- Updated all documentation to use `MYSQL_DB` consistently
- Fixed `docker-compose.yml` to use `MYSQL_DB`
- Fixed `Makefile` db-init to use `MYSQL_DB`

### **Type Conversion**
- Fixed `common/env_readers.py` to auto-cast env vars to correct types (int, float, bool)
- Now `REQUEST_TIMEOUT_SECONDS=30` is cast to `int(30)` automatically

---

## 📦 **Files Summary**

### **New Files (13)**
1. `agentic/schemas.py`
2. `agentic/quality.py`
3. `pipelines/agentic_controller.py`
4. `configs/agentic.yaml`
5. `db/migrations/2025_10_14_agentic_plan_and_iter.sql`
6. `scripts/run_agentic.py`
7. `scripts/view_agentic_iters.py`
8. `run_agentic.bat`
9. `scripts/run_agentic.sh`
10. `examples/agentic_plan_example.json`
11. `AGENTIC_QUICKSTART.md`
12. `AGENTIC_CHEATSHEET.md`
13. `TEST_AGENTIC.md`

Plus tests:
14. `tests/test_agentic_plan.py`
15. `tests/test_agentic_quality.py`

### **Modified Files (8)**
1. `agentic/llm.py`
2. `db/dao.py`
3. `apps/api/main.py`
4. `common/settings.py`
5. `Makefile`
6. `docker-compose.yml`
7. `README.md`
8. Plus documentation files (QUICK_REFERENCE, START_HERE, etc.)

---

## 🎯 **Impact**

### **Before**
- Linear search: Query → Results → Cache
- Manual query crafting
- No quality filtering beyond basic scoring
- No iteration or refinement
- No audit trail

### **After**
- ✅ Autonomous agentic loop
- ✅ LLM-generated search strategy
- ✅ Multi-layered quality gates
- ✅ Iterative refinement with new queries
- ✅ Full regulatory-compliant audit
- ✅ CLI + API + VSCode debug support
- ✅ Stop conditions (budget, goals, progress)

---

## 📊 **Metrics**

- **Lines of Code:** ~1,800+ new
- **Tests:** 16+ new test cases
- **API Endpoints:** 3 new
- **Database Tables:** 2 new (audit)
- **CLI Commands:** 3 new (run, view, dry-run)
- **VSCode Configs:** 12 debug configurations
- **Documentation Pages:** 4 new guides

---

## 🏆 **Breaking Changes**

### **None! Fully Backward Compatible**

- Old `search_pipeline.py` still works
- Old `ingest_pipeline.py` unchanged (except improvements)
- New agentic system is additive

### **Required Actions**

1. **Update `.env`:**
   ```bash
   # Change from (if you had this):
   MYSQL_DATABASE=reg_cache
   
   # To:
   MYSQL_DB=reg_cache
   ```

2. **Run migrations:**
   ```bash
   make migrate-agentic
   ```

3. **Install if needed:**
   ```bash
   pip install -r requirements.txt
   # (adds trafilatura, beautifulsoup4, lxml - already in requirements.txt)
   ```

---

## 🚀 **Upgrade Path**

### **From v1.x to v2.0:**

```bash
# 1. Pull changes
git pull origin main

# 2. Update .env (MYSQL_DATABASE → MYSQL_DB if needed)
nano .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
make migrate
make migrate-agentic

# 5. Test
python scripts/run_agentic.py --prompt "Test" --dry-run

# 6. Go live!
make agentic-example
```

---

## 📖 **Documentation**

- **[AGENTIC_QUICKSTART.md](AGENTIC_QUICKSTART.md)** - Complete tutorial
- **[AGENTIC_CHEATSHEET.md](AGENTIC_CHEATSHEET.md)** - Quick reference
- **[TEST_AGENTIC.md](TEST_AGENTIC.md)** - Testing & debugging guide
- **[README.md](README.md)** - Updated with full Agentic section
- **[examples/agentic_plan_example.json](examples/agentic_plan_example.json)** - Ready-to-use plan

---

## 🙏 **Credits**

This release transforms the project from a simple search pipeline into a **production-grade agentic system** suitable for regulatory compliance in healthcare.

**Key Innovations:**
- Multi-agent architecture (Planner + Judge + Controller)
- Quality gates with semantic + hard filters
- Full audit trail for regulatory compliance
- Cost control with budgets and stop conditions
- Human-in-the-loop capability (editable plans)

---

## 📅 **Next Steps (Future)**

- [ ] `/agentic/dry-run` endpoint (simulate without DB)
- [ ] Simple web UI for plan visualization
- [ ] Auto-enqueue approved docs for ingestion
- [ ] Backfill anchor_signals for legacy records
- [ ] Prometheus metrics for monitoring
- [ ] Multi-agent orchestration (parallel judges)

---

**Version 2.0.0 - From Linear Search to Autonomous AI! 🤖🚀**


````

## [8] CONTRIBUTING.md

````markdown
# FILE: CONTRIBUTING.md
# FULL: C:\Projetos\agentic-reg-ingest\CONTRIBUTING.md
# NOTE: Concatenated snapshot for review
# Contributing to agentic-reg-ingest

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/agentic-reg-ingest.git
   cd agentic-reg-ingest
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   make deps
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Follow existing code style
   - Add docstrings to functions/classes
   - Update tests as needed

3. **Run linters**
   ```bash
   make lint
   ```

4. **Run tests**
   ```bash
   make test
   ```

5. **Run type checker**
   ```bash
   make typecheck
   ```

## Code Style

- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking
- Use type hints where possible
- Write descriptive variable names
- Keep functions focused and single-purpose

## Testing Guidelines

- Write tests for new features
- Maintain or improve test coverage
- Use pytest fixtures for setup/teardown
- Mock external dependencies (APIs, databases)
- Test edge cases and error conditions

## Commit Messages

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Example:
```
feat: add support for Excel file ingestion

- Add Excel parser using openpyxl
- Update router to handle .xlsx files
- Add tests for Excel ingestion

Closes #123
```

## Pull Request Process

1. Update documentation (README, docstrings) if needed
2. Ensure all tests pass
3. Update CHANGELOG.md with your changes
4. Submit PR with clear description of changes
5. Link related issues
6. Wait for review and address feedback

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

Thank you for contributing! 🎉


````

## [9] DEBUG_GUIDE.md

````markdown
# FILE: DEBUG_GUIDE.md
# FULL: C:\Projetos\agentic-reg-ingest\DEBUG_GUIDE.md
# NOTE: Concatenated snapshot for review
# Guia de Debug no VSCode/Cursor

## 🚀 Como Debugar a Search Pipeline

### Passo 1: Configurar o .env

Antes de debugar, certifique-se de que o arquivo `.env` existe e está configurado:

```bash
# Se ainda não existe, copie o exemplo
cp .env.example .env
```

Edite o `.env` e configure:
```env
GOOGLE_API_KEY=sua-chave-google-aqui
GOOGLE_CX=seu-custom-search-id-aqui
OPENAI_API_KEY=sk-sua-chave-openai
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=reg_cache
MYSQL_USER=root
MYSQL_PASSWORD=sua-senha
```

### Passo 2: Garantir que o MySQL está rodando

```bash
# Via Docker
docker compose up -d mysql

# Verificar se está rodando
docker compose ps
```

### Passo 3: Inicializar o banco (primeira vez)

```bash
# No terminal do VSCode (Ctrl+`)
make db-init

# OU manualmente
python -c "from db.session import init_db; from common.env_readers import load_yaml_with_env; init_db(load_yaml_with_env('configs/db.yaml'))"
```

### Passo 4: Debugar a Search Pipeline

1. **Abra o arquivo** `pipelines/search_pipeline.py`

2. **Coloque breakpoints** clicando à esquerda do número da linha (aparece um círculo vermelho)
   - Sugestões de breakpoints:
     - Linha ~87: `def execute()`
     - Linha ~100: após carregar cache
     - Linha ~115: após executar CSE
     - Linha ~135: após calcular score

3. **Abra o painel de Debug**:
   - Pressione `Ctrl+Shift+D` (Windows/Linux)
   - Ou `Cmd+Shift+D` (Mac)
   - Ou clique no ícone de "play com bug" na barra lateral

4. **Selecione a configuração**: 
   - No dropdown do topo, escolha **"Debug: Search Pipeline"**

5. **Inicie o debug**:
   - Pressione `F5` ou clique no botão verde "▶ Start Debugging"

6. **Controles do Debug**:
   - `F5` - Continue (continuar até próximo breakpoint)
   - `F10` - Step Over (executar linha atual)
   - `F11` - Step Into (entrar na função)
   - `Shift+F11` - Step Out (sair da função)
   - `Ctrl+Shift+F5` - Restart
   - `Shift+F5` - Stop

### Passo 5: Inspecionar Variáveis

Durante o debug, você pode:

- **Ver variáveis locais**: Painel "Variables" à esquerda
- **Avaliar expressões**: Painel "Watch" - adicione expressões para monitorar
- **Console interativo**: Painel "Debug Console" - execute comandos Python
- **Call Stack**: Ver a pilha de chamadas

## 🔍 Exemplo de Debug Session

```python
# Ao pausar no breakpoint dentro de execute():

# No Debug Console, você pode:
>>> cache_key
'a3f5b8c9d1e2...'

>>> len(items)
10

>>> items[0]['title']
'Resolução Normativa 259'

>>> self.scorer.score(...)
3.456
```

## 📝 Dicas Úteis

### Mudar a Query de Busca

Edite em `.vscode/launch.json`:
```json
"args": [
    "--query", "TISS ANS",  // <-- Mude aqui
    "--topn", "20"          // <-- Ou limite de resultados
]
```

### Debug com menos resultados

Para testar mais rápido, reduza o `--topn`:
```json
"args": [
    "--query", "RN 259 ANS",
    "--topn", "5"  // <-- Apenas 5 resultados
]
```

### Debug Condicional

Clique com botão direito no breakpoint → "Edit Breakpoint" → "Conditional":
```python
# Parar apenas quando score > 3.0
score > 3.0

# Parar apenas para domínios .gov.br
'.gov.br' in url

# Parar na 10ª iteração
idx == 9
```

### Logpoints

Em vez de breakpoint, adicione um "Logpoint" (não para a execução):
- Botão direito → "Add Logpoint"
- Digite: `Score: {score}, URL: {url}`

## 🐛 Outras Configurações de Debug

### Debug: Ingest Pipeline
```
Executa a pipeline de ingestão
Útil para debugar processamento de PDFs/ZIPs/HTML
```

### Debug: FastAPI Server
```
Inicia servidor FastAPI em modo debug
Breakpoints funcionam ao fazer requisições HTTP
```

### Debug: Current Python File
```
Debuga o arquivo Python atualmente aberto
Útil para testar módulos individuais
```

### Debug: Pytest
```
Debuga testes unitários
Escolha "Debug: Pytest Current File" ou "Debug: All Tests"
```

## 🆘 Troubleshooting

### Erro: "No module named 'agentic'"
- Certifique-se de que está usando o interpretador do `.venv`
- Pressione `Ctrl+Shift+P` → "Python: Select Interpreter" → escolha `.venv/bin/python`

### Erro: "Missing GOOGLE_API_KEY"
- Verifique se o arquivo `.env` existe
- Verifique se as variáveis estão definidas corretamente

### Erro: "Can't connect to MySQL"
- Verifique se o MySQL está rodando: `docker compose ps`
- Verifique as credenciais em `.env`
- Teste conexão: `mysql -h localhost -u root -p`

### Debug muito lento
- Use `--topn 5` para menos resultados
- Desabilite "justMyCode": false para debugar bibliotecas externas
- Use Logpoints em vez de Breakpoints onde possível

## 📊 Monitorando a Execução

### Ver logs estruturados
Os logs JSON aparecem no terminal integrado. Para melhor visualização:

```bash
# Instalar jq (JSON processor)
# Windows (via chocolatey)
choco install jq

# Linux
sudo apt install jq

# Mac
brew install jq

# Então você pode filtrar logs:
python pipelines/search_pipeline.py ... | jq .
```

### Verificar o banco de dados

```bash
# Conectar ao MySQL
docker compose exec mysql mysql -u root -p reg_cache

# Ver queries em cache
SELECT * FROM search_query ORDER BY created_at DESC LIMIT 5;

# Ver resultados
SELECT url, title, score FROM search_result ORDER BY score DESC LIMIT 10;
```

---

**Pronto para debugar! 🚀**

Pressione `F5` e comece a explorar o código em tempo real!


````

## [10] DEBUG_WEB_UI.md

````markdown
# FILE: DEBUG_WEB_UI.md
# FULL: C:\Projetos\agentic-reg-ingest\DEBUG_WEB_UI.md
# NOTE: Concatenated snapshot for review
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


````

## [11] DigiCertGlobalRootCA.crt.pem

```
// FILE: DigiCertGlobalRootCA.crt.pem
// FULL: C:\Projetos\agentic-reg-ingest\DigiCertGlobalRootCA.crt.pem
// NOTE: Concatenated snapshot for review
-----BEGIN CERTIFICATE-----
MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBD
QTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IENBMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4jvhEXLeqKTTo1eqUKKPC3eQyaKl7hLOllsB
CSDMAZOnTjC3U/dDxGkAV53ijSLdhwZAAIEJzs4bg7/fzTtxRuLWZscFs3YnFo97
nh6Vfe63SKMI2tavegw5BmV/Sl0fvBf4q77uKNd0f3p4mVmFaG5cIzJLv07A6Fpt
43C/dxC//AH2hdmoRBBYMql1GNXRor5H4idq9Joz+EkIYIvUX7Q6hL+hqkpMfT7P
T19sdl6gSzeRntwi5m3OFBqOasv+zbMUZBfHWymeMr/y7vrTC0LUq7dBMtoM1O/4
gdW7jVg/tRvoSSiicNoxBN33shbyTApOB6jtSj1etX+jkMOvJwIDAQABo2MwYTAO
BgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUA95QNVbR
TLtm8KPiGxvDl7I90VUwHwYDVR0jBBgwFoAUA95QNVbRTLtm8KPiGxvDl7I90VUw
DQYJKoZIhvcNAQEFBQADggEBAMucN6pIExIK+t1EnE9SsPTfrgT1eXkIoyQY/Esr
hMAtudXH/vTBH1jLuG2cenTnmCmrEbXjcKChzUyImZOMkXDiqw8cvpOp/2PV5Adg
06O/nVsJ8dWO41P0jmP6P6fbtGbfYmbW0W5BjfIttep3Sp+dWOIrWcBAI+0tKIJF
PnlUkiaY4IBIqDfv8NZ5YBberOgOzW6sRBc4L0na4UU+Krk2U886UAb3LujEV0ls
YSEY1QSteDwsOoBrp+uvFRTp2InBuThs4pFsiv9kuXclVzDAGySj4dzp30d8tbQk
CAUw7C29C79Fv1C5qfPrmAESrciIxpg0X40KPMbp1ZWVbd4=
-----END CERTIFICATE-----

```

## [12] Dockerfile

```
// FILE: Dockerfile
// FULL: C:\Projetos\agentic-reg-ingest\Dockerfile
// NOTE: Concatenated snapshot for review
# Dockerfile for agentic-reg-ingest

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/downloads data/output

# Expose port
EXPOSE 8000

# Default command: run FastAPI server
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


```

## [13] LICENSE

```
// FILE: LICENSE
// FULL: C:\Projetos\agentic-reg-ingest\LICENSE
// NOTE: Concatenated snapshot for review
MIT License

Copyright (c) 2024 agentic-reg-ingest

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


```

## [14] Makefile

```
// FILE: Makefile
// FULL: C:\Projetos\agentic-reg-ingest\Makefile
// NOTE: Concatenated snapshot for review
.PHONY: help venv deps lock db-init migrate migrate-agentic search ingest agentic-example agentic-view ui api lint test typecheck clean

help:
	@echo "Agentic Regulatory Ingest - Make targets"
	@echo ""
	@echo "Setup:"
	@echo "  make venv        - Create virtual environment"
	@echo "  make deps        - Install dependencies"
	@echo "  make lock        - Lock dependencies (requires pip-tools)"
	@echo "  make db-init         - Initialize database schema"
	@echo "  make migrate         - Run typing migrations"
	@echo "  make migrate-agentic - Run agentic search migrations"
	@echo ""
	@echo "Pipelines:"
	@echo "  make search          - Run search pipeline"
	@echo "  make ingest          - Run ingest pipeline"
	@echo "  make agentic-example - Run agentic search with example plan"
	@echo "  make agentic-view    - View agentic iterations (set PLAN_ID=...)"
	@echo ""
	@echo "Development:"
	@echo "  make ui          - Start API + open web console"
	@echo "  make api         - Start FastAPI server"
	@echo "  make lint        - Run linters (ruff + black)"
	@echo "  make test        - Run tests"
	@echo "  make typecheck   - Run type checker (mypy)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Clean generated files"

venv:
	python3.11 -m venv .venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)"

deps:
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

lock:
	@if command -v pip-compile >/dev/null 2>&1; then \
		pip-compile requirements.in --output-file requirements.txt; \
		echo "Dependencies locked to requirements.txt"; \
	else \
		echo "pip-tools not installed. Run: pip install pip-tools"; \
		exit 1; \
	fi

db-init:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Copy .env.example to .env and configure."; \
		exit 1; \
	fi
	@echo "Initializing database schema..."
	@.venv/bin/python -c "from db.session import init_db; from common.env_readers import load_yaml_with_env; init_db(load_yaml_with_env('configs/db.yaml'))" || \
	mysql -h$$(grep MYSQL_HOST .env | cut -d '=' -f2) \
	      -P$$(grep MYSQL_PORT .env | cut -d '=' -f2) \
	      -u$$(grep MYSQL_USER .env | cut -d '=' -f2) \
	      -p$$(grep MYSQL_PASSWORD .env | cut -d '=' -f2) \
	      $$(grep MYSQL_DB .env | cut -d '=' -f2) < db/schema.sql
	@echo "Database initialized."

migrate:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Configure database credentials first."; \
		exit 1; \
	fi
	@echo "Running typing migrations..."
	@mysql --host=$$(grep MYSQL_HOST .env | cut -d '=' -f2) \
	       --port=$$(grep MYSQL_PORT .env | cut -d '=' -f2) \
	       -u$$(grep MYSQL_USER .env | cut -d '=' -f2) \
	       -p$$(grep MYSQL_PASSWORD .env | cut -d '=' -f2) \
	       $$(grep MYSQL_DB .env | cut -d '=' -f2) < db/migrations/2025_10_14_add_typing_columns.sql
	@echo "Typing migration complete."

migrate-agentic:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Configure database credentials first."; \
		exit 1; \
	fi
	@echo "Running agentic search migrations..."
	@mysql --host=$$(grep MYSQL_HOST .env | cut -d '=' -f2) \
	       --port=$$(grep MYSQL_PORT .env | cut -d '=' -f2) \
	       -u$$(grep MYSQL_USER .env | cut -d '=' -f2) \
	       -p$$(grep MYSQL_PASSWORD .env | cut -d '=' -f2) \
	       $$(grep MYSQL_DB .env | cut -d '=' -f2) < db/migrations/2025_10_14_agentic_plan_and_iter.sql
	@echo "Agentic migration complete."

search:
	.venv/bin/python pipelines/search_pipeline.py \
		--config configs/cse.yaml \
		--db configs/db.yaml \
		--query "RN 259 ANS" \
		--topn 100

ingest:
	.venv/bin/python pipelines/ingest_pipeline.py \
		--config configs/ingest.yaml \
		--db configs/db.yaml \
		--limit 100

agentic-example:
	@echo "Running agentic search with example plan..."
	.venv/bin/python scripts/run_agentic.py \
		--plan-file examples/agentic_plan_example.json \
		--debug

agentic-view:
	@if [ -z "$(PLAN_ID)" ]; then \
		echo "Usage: make agentic-view PLAN_ID=<uuid>"; \
		exit 1; \
	fi
	.venv/bin/python scripts/view_agentic_iters.py $(PLAN_ID)

ui:
	@echo "========================================="
	@echo "  🌐 Agentic Search Console"
	@echo "========================================="
	@echo ""
	@echo "Starting API server..."
	@echo "Open in browser: http://localhost:8000/ui"
	@echo ""
	@echo "Press Ctrl+C to stop"
	@echo ""
	.venv/bin/uvicorn apps.api.main:app --reload --port 8000

api:
	.venv/bin/uvicorn apps.api.main:app --reload --port 8000

lint:
	.venv/bin/ruff check .
	.venv/bin/black --check .

test:
	.venv/bin/pytest tests/ -v

typecheck:
	.venv/bin/mypy --ignore-missing-imports --no-strict-optional agentic/ pipelines/ apps/ db/ common/ ingestion/ vector/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf data/downloads/* data/output/*


```

## [15] QUICKSTART_CHECKLIST.md

````markdown
# FILE: QUICKSTART_CHECKLIST.md
# FULL: C:\Projetos\agentic-reg-ingest\QUICKSTART_CHECKLIST.md
# NOTE: Concatenated snapshot for review
# ✅ Checklist de Setup Rápido

Use este checklist para garantir que tudo está configurado antes de rodar o debug.

## 📋 Passo a Passo

### ☐ 1. Virtual Environment

```bash
# Criar .venv (se ainda não existe)
python3.11 -m venv .venv

# Windows PowerShell
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Confirmar que está ativo (deve mostrar (.venv) no prompt)
```

**✅ Checkpoint**: O prompt deve mostrar `(.venv)` no início

---

### ☐ 2. Instalar Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

**✅ Checkpoint**: Rodar `pip list` deve mostrar fastapi, sqlalchemy, openai, etc.

---

### ☐ 3. Configurar .env

```bash
# Copiar exemplo
cp .env.example .env

# Editar .env com suas credenciais
code .env  # ou use seu editor favorito
```

**Variáveis OBRIGATÓRIAS para Search Pipeline**:
```env
GOOGLE_API_KEY=sua-chave-aqui       # ← Obtenha em: https://console.cloud.google.com/
GOOGLE_CX=seu-cx-aqui                # ← Custom Search Engine ID
OPENAI_API_KEY=sk-xxx                # ← API key da OpenAI
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=reg_cache
MYSQL_USER=root
MYSQL_PASSWORD=sua-senha-mysql
```

**✅ Checkpoint**: Arquivo `.env` existe e tem todas as variáveis preenchidas

---

### ☐ 4. MySQL via Docker

```bash
# Iniciar MySQL
docker compose up -d mysql

# Verificar status
docker compose ps

# Aguardar ~10 segundos para MySQL inicializar
```

**✅ Checkpoint**: `docker compose ps` mostra mysql como "Up" e "healthy"

---

### ☐ 5. Inicializar Banco de Dados

```bash
# Opção 1: Via Makefile
make db-init

# Opção 2: Via Python
python -c "from db.session import init_db; from common.env_readers import load_yaml_with_env; init_db(load_yaml_with_env('configs/db.yaml'))"

# Opção 3: Via MySQL CLI
docker compose exec mysql mysql -u root -p${MYSQL_PASSWORD} reg_cache < db/schema.sql
```

**✅ Checkpoint**: Não deve ter erros. Tabelas criadas com sucesso.

**Verificar tabelas**:
```bash
docker compose exec mysql mysql -u root -p${MYSQL_PASSWORD} reg_cache -e "SHOW TABLES;"
```

Deve mostrar:
```
+----------------------+
| Tables_in_reg_cache  |
+----------------------+
| document_catalog     |
| search_query         |
| search_result        |
+----------------------+
```

---

### ☐ 6. Selecionar Interpretador Python no VSCode

1. Pressione `Ctrl+Shift+P` (ou `Cmd+Shift+P` no Mac)
2. Digite: `Python: Select Interpreter`
3. Escolha: `.venv/bin/python` ou `.venv\Scripts\python.exe`

**✅ Checkpoint**: Barra de status inferior mostra `.venv` como interpretador

---

### ☐ 7. Testar Credenciais (Opcional mas Recomendado)

```bash
# Testar Google CSE
python -c "
from common.settings import settings
print(f'Google API Key: {settings.google_api_key[:10]}...')
print(f'Google CX: {settings.google_cx}')
"

# Testar OpenAI
python -c "
from common.settings import settings
print(f'OpenAI Key: {settings.openai_api_key[:10]}...')
"
```

**✅ Checkpoint**: Deve imprimir os primeiros caracteres das chaves (não "your-key-here")

---

## 🎯 Pronto para Debugar!

Se todos os checkpoints acima passaram, você está pronto! 

### Iniciar Debug da Search Pipeline:

1. Abra `pipelines/search_pipeline.py`
2. Coloque um breakpoint na linha ~87 (função `execute`)
3. Pressione `F5`
4. Selecione **"Debug: Search Pipeline"**
5. Observe a execução pausar no breakpoint!

---

## 🚨 Troubleshooting Rápido

### Erro: "ModuleNotFoundError"
```bash
# Reinstalar dependências
pip install -r requirements.txt

# Verificar PYTHONPATH
export PYTHONPATH=$PWD  # Linux/Mac
$env:PYTHONPATH = $PWD  # Windows PowerShell
```

### Erro: "Can't connect to database"
```bash
# Reiniciar MySQL
docker compose restart mysql

# Aguardar 10 segundos
sleep 10

# Testar conexão
docker compose exec mysql mysql -u root -p -e "SELECT 1;"
```

### Erro: "Invalid API key"
```bash
# Verificar se .env está sendo lido
python -c "from common.settings import settings; print(settings.google_api_key)"

# Se aparecer "your-google-api-key-here", o .env não está configurado
```

### MySQL não inicia
```bash
# Ver logs
docker compose logs mysql

# Remover volume e reiniciar (⚠️ apaga dados)
docker compose down -v
docker compose up -d mysql
```

---

## 📞 Precisa de Ajuda?

Abra uma issue no GitHub ou consulte:
- `README.md` - Documentação completa
- `DEBUG_GUIDE.md` - Guia detalhado de debug
- `CONTRIBUTING.md` - Guidelines de contribuição

**Boa sorte! 🚀**


````

## [16] QUICK_REFERENCE.md

````markdown
# FILE: QUICK_REFERENCE.md
# FULL: C:\Projetos\agentic-reg-ingest\QUICK_REFERENCE.md
# NOTE: Concatenated snapshot for review
# 🚀 Referência Rápida - agentic-reg-ingest

## ⚡ Comandos Mais Usados

### Setup Inicial
```bash
python3.11 -m venv .venv                    # Criar venv
source .venv/bin/activate                   # Ativar (Linux/Mac)
.venv\Scripts\activate                      # Ativar (Windows)
pip install -r requirements.txt             # Instalar deps
cp .env.example .env                        # Criar .env
docker compose up -d mysql                  # Iniciar MySQL
make db-init                                # Criar tabelas
```

### Rodar Pipelines
```bash
make search                                 # Pipeline de busca
make ingest                                 # Pipeline de ingestão
make api                                    # Servidor FastAPI
```

### Debug no VSCode/Cursor
```
1. Ctrl+Shift+D (abrir debug)
2. Selecionar "Debug: Search Pipeline"
3. F5 (iniciar)
4. F10 (step over), F11 (step into)
```

### Testes e Qualidade
```bash
make test                                   # Rodar testes
make lint                                   # Linters
make typecheck                              # Type checking
```

---

## 📁 Estrutura do Projeto

```
agentic-reg-ingest/
├── apps/api/                 → FastAPI endpoints
│   ├── main.py              → Aplicação principal
│   └── middleware.py        → Logging middleware
│
├── agentic/                  → Core search & AI
│   ├── cse_client.py        → Google CSE
│   ├── scoring.py           → Score algorithm
│   ├── normalize.py         → URL normalization
│   └── llm.py               → OpenAI wrapper
│
├── pipelines/                → Pipeline orchestration
│   ├── search_pipeline.py   → 🔍 PIPELINE 1
│   ├── ingest_pipeline.py   → 📥 PIPELINE 2
│   ├── routers.py           → Document router
│   └── executors/           → Type-specific processors
│       ├── pdf_ingestor.py  → PDF processing
│       ├── zip_ingestor.py  → ZIP/tables
│       └── html_ingestor.py → HTML extraction
│
├── ingestion/                → Chunking & embedding prep
│   ├── anchors.py           → Anchor detection
│   ├── chunkers.py          → Token-aware chunking
│   └── emitters.py          → JSONL output
│
├── db/                       → Database layer
│   ├── schema.sql           → MySQL schema
│   ├── models.py            → SQLAlchemy models
│   ├── session.py           → Session management
│   └── dao.py               → Data access objects
│
├── common/                   → Shared utilities
│   ├── settings.py          → Pydantic settings
│   └── env_readers.py       → YAML + ${VAR} loader
│
├── configs/                  → Configuration files
│   ├── cse.yaml             → Search config
│   ├── db.yaml              → Database config
│   └── ingest.yaml          → Ingest config
│
├── vector/                   → Vector database
│   ├── qdrant_loader.py     → Load to Qdrant
│   └── settings.yaml        → Qdrant config
│
└── tests/                    → Test suite
    ├── test_scoring.py      → Scoring tests
    ├── test_router_llm.py   → Router tests
    └── test_pdf_markers.py  → Anchor tests
```

---

## 🔑 Variáveis de Ambiente (.env)

```env
# Obrigatórias
GOOGLE_API_KEY=xxx              # Google Cloud Console
GOOGLE_CX=xxx                   # Custom Search Engine ID
OPENAI_API_KEY=sk-xxx           # OpenAI API
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=xxx
MYSQL_DB=reg_cache

# Opcionais
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
REQUEST_TIMEOUT_SECONDS=30      # Timeout HTTP
TTL_DAYS=7                      # Cache TTL
QDRANT_URL=http://localhost:6333
```

---

## 🎯 Fluxo das Pipelines

### Pipeline 1: Search
```
Query → Google CSE → Normalize URLs → HEAD requests → Score → Rank → MySQL Cache
                                                                      ↓
                                                            Update document_catalog
```

### Pipeline 2: Ingest
```
DB (NEW/CHANGED) → Route (PDF/ZIP/HTML) → Download → Process → Chunk → JSONL
                           ↓
                    LLM sugere markers → Anchor detection → Smart chunking
```

---

## 🔍 Breakpoints Úteis

### search_pipeline.py
- **Linha ~87**: `def execute()` - Início da pipeline
- **Linha ~100**: Após verificar cache
- **Linha ~115**: Após chamar Google CSE
- **Linha ~130**: Loop de scoring

### ingest_pipeline.py
- **Linha ~70**: `def execute()` - Início
- **Linha ~85**: Loop de documentos
- **Linha ~95**: Routing decision
- **Linha ~105**: Chamada ao ingestor

### pdf_ingestor.py
- **Linha ~78**: `def ingest()` - Início
- **Linha ~85**: Download PDF
- **Linha ~90**: Extract text
- **Linha ~100**: LLM marker suggestion

---

## 📊 Consultas MySQL Úteis

```sql
-- Ver queries em cache
SELECT cache_key, query_text, result_count, created_at 
FROM search_query 
ORDER BY created_at DESC 
LIMIT 10;

-- Top 10 resultados por score
SELECT sr.url, sr.title, sr.score, sq.query_text
FROM search_result sr
JOIN search_query sq ON sr.query_id = sq.id
ORDER BY sr.score DESC
LIMIT 10;

-- Documentos prontos para ingestão
SELECT canonical_url, title, ingest_status, last_checked_at
FROM document_catalog
WHERE ingest_status = 'pending'
ORDER BY last_checked_at DESC;

-- Estatísticas
SELECT 
    ingest_status, 
    COUNT(*) as count 
FROM document_catalog 
GROUP BY ingest_status;
```

---

## 🐳 Docker Commands

```bash
# Iniciar serviços
docker compose up -d                    # Todos
docker compose up -d mysql              # Só MySQL
docker compose up -d qdrant             # Só Qdrant

# Status
docker compose ps

# Logs
docker compose logs -f api
docker compose logs -f mysql

# Parar
docker compose stop
docker compose down                     # Para e remove containers
docker compose down -v                  # Para e remove volumes (⚠️ apaga dados)

# Shell no container
docker compose exec mysql bash
docker compose exec mysql mysql -u root -p reg_cache
```

---

## 🌐 API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Search
curl -X POST http://localhost:8000/run/search \
  -H "Content-Type: application/json" \
  -d '{"query": "RN 259 ANS", "topn": 50}'

# Ingest
curl -X POST http://localhost:8000/run/ingest \
  -H "Content-Type: application/json" \
  -d '{"limit": 20}'

# Docs
open http://localhost:8000/docs          # Swagger UI
```

---

## 🧪 Testes

```bash
# Todos os testes
pytest tests/ -v

# Arquivo específico
pytest tests/test_scoring.py -v

# Teste específico
pytest tests/test_scoring.py::test_score_authority_gov_domain -v

# Com coverage
pytest tests/ --cov=. --cov-report=html

# Apenas testes rápidos (excluir slow)
pytest -m "not slow"
```

---

## 📦 Arquivos de Output

```
data/
├── downloads/              → PDFs/ZIPs baixados
│   ├── 12345.pdf
│   └── 67890.zip
│
└── output/                 → Knowledge base
    └── kb_regulatory.jsonl → Chunks prontos para embedding
```

---

## 🎨 Atalhos do VSCode/Cursor

| Atalho | Ação |
|--------|------|
| `F5` | Start debugging |
| `Ctrl+Shift+D` | Abrir debug panel |
| `F9` | Toggle breakpoint |
| `F10` | Step over |
| `F11` | Step into |
| `Shift+F11` | Step out |
| `Ctrl+Shift+F5` | Restart debug |
| `Ctrl+` ` | Toggle terminal |
| `Ctrl+Shift+P` | Command palette |

---

## 🔧 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Can't connect to DB | `docker compose restart mysql` |
| Invalid API key | Verificar `.env` |
| Import errors | Verificar interpretador Python (.venv) |
| Port 8000 in use | `lsof -ti:8000 \| xargs kill` (Mac/Linux) |

---

## 📚 Documentação Adicional

- `README.md` - Documentação completa
- `DEBUG_GUIDE.md` - Guia detalhado de debug
- `QUICKSTART_CHECKLIST.md` - Checklist de setup
- `CONTRIBUTING.md` - Como contribuir
- `CHANGELOG.md` - Histórico de mudanças

---

**💡 Dica**: Mantenha este arquivo aberto em uma aba para consulta rápida!


````

## [17] README.md

````markdown
# FILE: README.md
# FULL: C:\Projetos\agentic-reg-ingest\README.md
# NOTE: Concatenated snapshot for review
# agentic-reg-ingest

Production-grade pipeline for searching and ingesting regulatory documents with intelligent chunking and vector storage.

## 🎯 Features

### Pipeline 1: Search & Cache
- Google Programmable Search Engine (CSE) integration
- Multi-factor scoring (authority, freshness, specificity, type, anchorability)
- MySQL caching with TTL
- Automatic URL normalization and metadata extraction

### Pipeline 2: Intelligent Ingestion
- Diff detection (NEW/CHANGED/SAME)
- LLM-powered intent routing (PDF/ZIP/HTML)
- PDF processing with LLM-suggested anchoring markers
- **HTML with LLM structure extraction** (sections, tables, anchors)
- PDF wrapper detection and re-routing
- Token-aware chunking with anchor alignment
- JSONL output for knowledge base
- Vector database (Qdrant) integration

## 🏗️ Architecture

```
agentic-reg-ingest/
├── apps/api/              # FastAPI REST endpoints
├── agentic/               # Core search & LLM clients
├── pipelines/             # Search & Ingest pipelines
│   └── executors/         # Type-specific ingestors
├── ingestion/             # Chunking, anchoring, emitting
├── db/                    # SQLAlchemy models & DAOs
├── common/                # Settings & config readers
├── configs/               # YAML configurations
├── vector/                # Qdrant loader
├── scripts/               # Helper scripts
└── tests/                 # Test suite
```

## 🎭 Typing & Routing

### Robust Document Type Detection

The pipeline uses a multi-layered detection strategy to accurately identify document types (PDF, ZIP, HTML) and prevent misrouting:

**Detection Priority (first match wins):**

1. **Magic Bytes** (highest priority) - Sniffs first 8 bytes via Range GET
   - `%PDF-` → PDF
   - `PK\x03\x04`, `PK\x05\x06`, `PK\x07\x08` → ZIP

2. **Content-Disposition** - Extracts filename from header
   - `filename="document.pdf"` → PDF

3. **Content-Type** - MIME type with URL extension disambiguation
   - `application/pdf` → PDF
   - `text/html` but URL ends in `.pdf` → PDF (trust extension)

4. **URL Extension** - Fallback to file extension
   - `.pdf`, `.zip`, `.html`

5. **Fallback** - Unknown (triggers LLM routing)

### Routing Strategy

**At Search Time** (`search_pipeline.py`):
- Detects type using all available signals
- Persists `final_type` to `search_result` and `document_catalog`
- Stores typing metadata: `http_content_type`, `detected_mime`, `url_ext`, `fetch_status`

**At Ingest Time** (`ingest_pipeline.py` → `routers.py`):
1. **Trust DB first** - If `final_type ∈ {pdf, zip, html}`, use it immediately
2. **Re-detect if unknown** - HEAD request + magic sniff
3. **LLM fallback** - Only if still unknown

**Executor Validation**:
- Each executor validates expected type before processing
- Fails fast if mismatch (e.g., PDF executor receives HTML)

### New Database Columns

**`search_result` table:**
```sql
http_content_type        VARCHAR(128)   -- Raw Content-Type header
http_content_disposition VARCHAR(255)   -- Content-Disposition header
url_ext                  VARCHAR(16)    -- URL extension (pdf, zip, html)
detected_mime            VARCHAR(128)   -- Detected MIME type
detected_ext             VARCHAR(16)    -- Detected extension
final_type               ENUM(...)      -- Final resolved type
fetch_status             ENUM(...)      -- ok, redirected, blocked, error
```

**`document_catalog` table:**
```sql
final_type               ENUM(...)      -- Cached type for routing
```

### Running Migrations

After pulling this update, run:

```bash
make migrate
```

Or manually:

```bash
mysql --host=$MYSQL_HOST --port=$MYSQL_PORT -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DB < db/migrations/2025_10_14_add_typing_columns.sql
```

## 🤖 Agentic Search (Plan→Act→Observe→Judge→Re-plan)

### Overview

**True agentic search** with autonomous loop that refines queries, applies quality gates, and only promotes high-quality, citable sources to the vector DB.

```
┌─────────────┐
│   PLAN      │ ← LLM generates search strategy
└──────┬──────┘
       ↓
┌─────────────┐
│    ACT      │ ← Execute queries via Google CSE
└──────┬──────┘
       ↓
┌─────────────┐
│  OBSERVE    │ ← Fetch metadata, detect types, score
└──────┬──────┘
       ↓
┌─────────────┐
│   JUDGE     │ ← Quality gates + LLM evaluation
└──────┬──────┘
       ↓
   ┌───────────┐     Stop?      ┌──────────┐
   │ Approved? │────────Yes─────→│   DONE   │
   └─────┬─────┘                 └──────────┘
         No
         ↓
   ┌───────────┐
   │  RE-PLAN  │ ← Merge new queries, iterate
   └─────┬─────┘
         │
         └───────→ (back to ACT)
```

### Key Features

**1. LLM Planner**
- Generates structured search plan from natural language prompt
- Outputs JSON with: goals, queries, quality gates, stop conditions
- Example prompt: *"Buscar todas as RNs da ANS sobre prazos de atendimento dos últimos 2 anos"*

**2. Agentic Loop**
- Executes 2-3 queries per iteration
- Fetches metadata and detects document types
- Applies **hard quality gates** (code-level)
- Asks LLM to **judge** candidates semantically
- Proposes **new queries** if gaps detected

**3. Quality Gates** (configurable)
```yaml
must_types: ["pdf", "zip"]      # Only official documents
max_age_years: 3                # Recent content only
min_anchor_signals: 1           # Must have Art./Anexo/Tabela
min_score: 0.65                 # Relevance threshold
```

**4. Stop Conditions**
- ✅ `min_approved` reached (e.g., 12 documents)
- ✅ `max_iterations` limit (e.g., 3)
- ✅ `budget` exceeded (max CSE calls)
- ✅ No progress (no approvals, no new queries)

**5. Full Audit Trail**
- Every iteration persisted to `agentic_plan` and `agentic_iter` tables
- Tracks: executed queries, approved URLs, rejected (with reasons), new queries
- Regulatory-compliant audit logs

### API Usage

#### Step 1: Create Plan

```bash
POST /agentic/plan
Content-Type: application/json

{
  "prompt": "Buscar RNs da ANS sobre cobertura obrigatória e prazos máximos de atendimento, publicadas nos últimos 2 anos"
}

Response:
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan": {
    "goal": "RNs ANS sobre cobertura e prazos (2023-2025)",
    "topics": ["cobertura obrigatória", "prazos atendimento"],
    "queries": [
      {"q": "RN ANS cobertura obrigatória", "why": "Base coverage rules", "k": 10},
      {"q": "RN ANS prazos máximos atendimento", "why": "Service timeline regulations", "k": 10}
    ],
    "allow_domains": ["www.gov.br/ans", "www.planalto.gov.br"],
    "deny_patterns": [".*blog.*", ".*noticia.*"],
    "stop": {"min_approved": 12, "max_iterations": 3, "max_queries_per_iter": 2},
    "quality_gates": {
      "must_types": ["pdf", "zip"],
      "max_age_years": 2,
      "min_anchor_signals": 1,
      "min_score": 0.7
    },
    "budget": {"max_cse_calls": 60, "ttl_days": 7}
  }
}
```

#### Step 2: (Optional) Edit Plan JSON

You can edit the returned plan JSON before execution:
- Add/remove queries
- Adjust quality gates
- Change stop conditions

#### Step 3: Execute Loop

```bash
POST /agentic/run
Content-Type: application/json

{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000"
}

# OR with custom plan:
{
  "plan_override": { ...edited_plan... }
}

Response:
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "iterations": 2,
  "approved_total": 15,
  "stopped_by": "min_approved",
  "promoted_urls": [
    "https://www.gov.br/ans/.../rn-395.pdf",
    "https://www.gov.br/ans/.../rn-428.pdf",
    ...
  ]
}
```

#### Step 4: Review Audit Trail

```bash
GET /agentic/iters/550e8400-e29b-41d4-a716-446655440000

Response:
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_iterations": 2,
  "iterations": [
    {
      "iter_num": 1,
      "executed_queries": ["RN ANS cobertura obrigatória", "RN ANS prazos máximos"],
      "approved_urls": ["https://.../rn-395.pdf", ...],
      "rejected": [
        {"url": "https://.../noticia-xyz", "reason": "Tipo não permitido", "violations": ["type:not_allowed"]}
      ],
      "new_queries": ["RN 259 ANS anexos"],
      "summary": "Iter 1: 8 approved, 12 rejected",
      "created_at": "2025-10-14T18:00:00"
    },
    {
      "iter_num": 2,
      "executed_queries": ["RN 259 ANS anexos"],
      "approved_urls": [...],
      "rejected": [...],
      "new_queries": [],
      "summary": "Iter 2: 7 approved, 3 rejected",
      "created_at": "2025-10-14T18:02:15"
    }
  ]
}
```

### Cost Control & Safety

**Budget Controls:**
- `max_cse_calls`: Hard limit on Google CSE API calls
- `ttl_days`: Cache TTL to avoid redundant searches
- `max_iterations`: Cap on loop iterations

**Safety Guardrails:**
- `allow_domains`: Whitelist official domains only
- `deny_patterns`: Blacklist blogs, news, forums
- Hard quality gates before LLM judge
- Deterministic LLM (temperature=0)

### Configuration

Default settings in `configs/agentic.yaml`:

```yaml
agentic:
  default_stop:
    min_approved: 12
    max_iterations: 3
    max_queries_per_iter: 2
  
  default_quality:
    must_types: ["pdf", "zip"]
    max_age_years: 3
    min_anchor_signals: 1
    min_score: 0.65
  
  budget:
    max_cse_calls: 60
    ttl_days: 7
```

### Why This is "True Agentic"

✅ **Autonomous Planning** - LLM generates search strategy  
✅ **Iterative Refinement** - Loops until goal achieved  
✅ **Self-Correction** - Judge rejects poor sources, proposes new queries  
✅ **Memory & State** - Tracks progress across iterations  
✅ **Goal-Oriented** - Stops when target reached or no progress  
✅ **Full Audit** - Every decision logged for compliance  

### Database Schema

Run migration:
```bash
make migrate-agentic
```

Creates tables:
- `agentic_plan` - Stores search plans (goals, queries, gates)
- `agentic_iter` - Audit trail of every iteration

### 🌐 Web UI (HTMX Console)

**Visual interface para operar o sistema via browser** - zero build, apenas HTML + HTMX!

```bash
# 1. Iniciar servidor
make ui

# 2. Abrir browser
http://localhost:8000/ui
```

**Features:**
- 🧠 **Gerar Plano** - Digite objetivo em linguagem natural, LLM gera plano
- ✏️ **Editar Plano** - Ajuste JSON antes de executar (queries, gates, domains)
- 🚀 **Executar Loop** - Roda Plan→Act→Observe→Judge→Re-plan com auto-refresh
- 📊 **Audit Trail** - Visualiza iterações em tempo real (refresh 3s)
- ✅ **Aprovados** - Lista documentos aprovados com links clicáveis
- 💾 **Download** - Exporta lista de aprovados como JSON
- ⚡ **Pipeline Shortcuts** - Botões rápidos para search/ingest

**Requisitos:** Nenhum! HTMX via CDN, HTML estático.

**Screenshots da UI:**

```
┌─────────────────────────────────────────────────┐
│ 🤖 Agentic Search Console                      │
│ Plan → Act → Observe → Judge → Re-plan | v2.0  │
├─────────────────────┬───────────────────────────┤
│ 1️⃣ Gerar Plano      │ 3️⃣ Iterações & Audit      │
│ [Textarea: prompt]  │ ┌─ ITERATION 1           │
│ [Gerar] [Exemplo]   │ │ ✅ 8 ✗ 5               │
│                     │ │ Queries: RN ANS...     │
│ Plan JSON editável  │ └─────────────────       │
│ [JSON textarea]     │                          │
├─────────────────────┤ ✅ Documentos Aprovados   │
│ 2️⃣ Executar Loop    │ • doc1.pdf              │
│ [plan_id input]     │ • doc2.pdf              │
│ [Executar]          │ [💾 Baixar Lista]       │
└─────────────────────┴───────────────────────────┘
```

### CLI Usage (Recommended for Development)

**Quick Start:**
```bash
# 1. Run with example plan
make agentic-example

# 2. Or create from prompt
python scripts/run_agentic.py --prompt "Buscar RNs da ANS sobre prazos de atendimento" --debug

# 3. View results
make agentic-view PLAN_ID=<uuid>
```

**Advanced Usage:**
```bash
# Generate plan only (for editing)
python scripts/run_agentic.py \
  --prompt "Buscar RNs ANS cobertura" \
  --plan-only \
  --output my_plan.json

# Edit my_plan.json manually, then:
python scripts/run_agentic.py --plan-file my_plan.json --debug

# Dry-run (simulate without DB)
python scripts/run_agentic.py --plan-file my_plan.json --dry-run
```

**See full guide:** [AGENTIC_QUICKSTART.md](AGENTIC_QUICKSTART.md)

## 📄 HTML Ingestion (LLM-Structured)

### Overview

HTML documents are processed through a sophisticated pipeline that uses **LLM to structure content** (not summarize) before chunking:

```
Download → Readability → PDF Wrapper Check → LLM Structure → Anchor-Aware Chunking → JSONL
```

### Key Features

**1. PDF Wrapper Detection**
- Detects HTML pages that are just wrappers for PDF files
- Checks: `<iframe>`, `<embed>`, `<meta refresh>`, download links
- Auto-routes to PDF ingestor when detected

**2. LLM Structure Extraction**
- **Does NOT summarize** - preserves all content in original order
- Extracts canonical JSON schema:
  ```json
  {
    "title": "Document Title",
    "language": "pt",
    "sections": [{"heading": "...", "text": "..."}],
    "tables": [{"caption": "...", "rows": 10}],
    "pdf_links": ["https://..."],
    "anchors": [{"type": "h1|h2|h3|h4|table", "value": "..."}]
  }
  ```
- Uses `gpt-4o-mini` with strict JSON mode
- Temperature = 0 for consistency

**3. Readability + trafilatura**
- Removes boilerplate (nav, ads, scripts)
- Extracts clean article text
- Collects headings and table markers
- Caps content to ~80k chars for LLM

**4. Anchor-Aware Chunking**
- Aligns chunk boundaries with headings/tables
- Respects min/max token limits
- Preserves semantic coherence

### Configuration

Enable/disable in `configs/ingest.yaml`:

```yaml
llm_html_extractor:
  enabled: true              # Set false for readability-only (no LLM cost)
  model: gpt-4o-mini
  max_chars: 120000          # Max chars to extract from HTML
  max_chars_llm: 80000       # Max chars sent to LLM
  temperature: 0
```

### Fallback Behavior

If `enabled: false`:
- Uses trafilatura/BeautifulSoup only
- No LLM calls (zero cost)
- Still collects basic anchors from headings
- Produces chunks without LLM-structured metadata

### Output Metadata

Each chunk includes:

```json
{
  "text": "...",
  "tokens": 450,
  "source_url": "https://...",
  "metadata": {
    "content_type": "text/html",
    "extracted_by": "llm+readability",
    "llm_model": "gpt-4o-mini",
    "language": "pt",
    "sections_count": 5,
    "anchors_count": 12,
    "anchors": [...]
  }
}
```

### PDF Wrapper Handling

When HTML ingestor detects a PDF wrapper:

1. Logs detection: `pdf_wrapper_detected`
2. Returns routing instruction: `{"next_type": "pdf", "next_url": "..."}`
3. Pipeline marks HTML as failed with note
4. PDF URL is logged for manual/automated re-processing

**Future enhancement:** Auto-enqueue detected PDF for ingestion.

## 📋 Requirements

- Python 3.11+
- MySQL 8.0+ (or Azure Database for MySQL)
- Google Custom Search API credentials
- OpenAI API key
- Qdrant (optional, for vector storage)
- **New:** trafilatura, BeautifulSoup4, lxml (for HTML extraction)

## 🚀 Quickstart

### Quick Links
- 📘 **[Agentic Search Quickstart](AGENTIC_QUICKSTART.md)** - Guia completo de uso
- 📄 **[Example Plan](examples/agentic_plan_example.json)** - Plano pronto para usar

## 🚀 Setup Básico

### 1. Clone and Setup

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required variables:
- `GOOGLE_API_KEY` - Google API key
- `GOOGLE_CX` - Custom Search Engine ID
- `OPENAI_API_KEY` - OpenAI API key
- `MYSQL_*` - Database credentials

### 3. Start Services (Docker)

```bash
# Start MySQL and Qdrant
docker compose up -d mysql qdrant

# Initialize database schema
make db-init
```

Alternatively, apply schema manually:
```bash
mysql -h localhost -u root -p reg_cache < db/schema.sql
```

### 4. Run Pipelines

#### Search Pipeline
```bash
# Using Makefile
make search

# Or directly
python pipelines/search_pipeline.py \
    --config configs/cse.yaml \
    --db configs/db.yaml \
    --query "RN 259 ANS" \
    --topn 100
```

#### Ingest Pipeline
```bash
# Using Makefile
make ingest

# Or directly
python pipelines/ingest_pipeline.py \
    --config configs/ingest.yaml \
    --db configs/db.yaml \
    --limit 100
```

### 5. Start API Server

```bash
# Using Makefile
make api

# Or directly
uvicorn apps.api.main:app --reload --port 8000
```

Access API at: http://localhost:8000

## 🔧 Development

### Run Tests
```bash
make test
# or
pytest tests/ -v
```

### Linting
```bash
make lint
# or
ruff check .
black --check .
```

### Type Checking
```bash
make typecheck
# or
mypy --ignore-missing-imports agentic/ pipelines/ apps/
```

### Dependency Management

Using `pip-tools` (optional):
```bash
# Install pip-tools
pip install pip-tools

# Update requirements.txt from requirements.in
make lock
# or
pip-compile requirements.in
```

## 📡 API Endpoints

### Health Check
```bash
GET /health

Response:
{
  "status": "ok",
  "db_ok": true,
  "cse_ready": true,
  "openai_ready": true
}
```

### Run Search Pipeline
```bash
POST /run/search
Content-Type: application/json

{
  "query": "RN 259 ANS",
  "topn": 100
}

Response:
{
  "results_count": 47,
  "message": "Search completed: 47 results found"
}
```

### Run Ingest Pipeline
```bash
POST /run/ingest
Content-Type: application/json

{
  "limit": 50
}

Response:
{
  "total": 50,
  "new": 30,
  "changed": 20,
  "success": 45,
  "failed": 5
}
```

## 🗂️ Configuration Files

### configs/cse.yaml
Google CSE settings, domain boosting, keyword patterns

### configs/db.yaml
MySQL connection, pool settings, TTL

### configs/ingest.yaml
LLM settings, chunking parameters, download config

### vector/settings.yaml
Qdrant connection, collection settings, embedding model

All configs support `${VAR}` placeholders resolved from `.env`

## 📊 Database Schema

### search_query
Cached search queries with TTL

### search_result
Individual search results with scoring

### document_catalog
Canonical document registry for diff detection

## 🎨 Vector Database (Optional)

Load chunks into Qdrant:

```bash
python vector/qdrant_loader.py \
    --config vector/settings.yaml \
    --input data/output/kb_regulatory.jsonl
```

Note: Update `vector/qdrant_loader.py` to use actual embedding model (e.g., sentence-transformers)

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker compose build

# Start all services
docker compose up -d

# View logs
docker compose logs -f api
```

### Production
For production, configure:
- Volume mounts for `data/`
- Environment variables via `.env`
- SSL/TLS for MySQL
- Reverse proxy (nginx) for API

## 🧪 Testing

Test suite includes:
- `test_scoring.py` - Scoring algorithm tests
- `test_router_llm.py` - Document routing tests
- `test_pdf_markers.py` - Anchor detection tests

Run with coverage:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

## 📝 Logging

All logs are JSON-formatted (structlog) with:
- ISO timestamps
- Trace IDs for request tracking
- No sensitive data (credentials masked)

Example log:
```json
{
  "event": "request_complete",
  "method": "POST",
  "path": "/run/search",
  "status_code": 200,
  "duration_ms": 1234.56,
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-10-14T10:30:00.123456Z"
}
```

## 🔒 Security

- **Never commit secrets** - Use `.env` (gitignored)
- **Fail fast** - App exits if required env vars missing
- **SQL injection protection** - SQLAlchemy ORM
- **Request validation** - Pydantic models
- **Rate limiting** - Consider adding to production API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linters: `make lint`
5. Run tests: `make test`
6. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Troubleshooting

### Database Connection Failed
- Check MySQL is running: `docker compose ps`
- Verify `.env` credentials
- Test connection: `mysql -h localhost -u user -p`

### Search Pipeline Fails
- Verify Google API key and CX in `.env`
- Check CSE quotas in Google Cloud Console
- Review logs for detailed errors

### Ingest Pipeline Hangs
- Check OpenAI API key
- Verify network connectivity
- Reduce `--limit` for testing

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📚 References

- [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/overview)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Vector Database](https://qdrant.tech/)

---

**Built with ❤️ for regulatory compliance and knowledge management**


````

## [18] SETUP_COMPLETO.md

````markdown
# FILE: SETUP_COMPLETO.md
# FULL: C:\Projetos\agentic-reg-ingest\SETUP_COMPLETO.md
# NOTE: Concatenated snapshot for review
# 🚀 Setup Completo - Do Zero ao Funcionando

## ⚡ **Quick Setup (5 minutos)**

```bash
# 1. Ativar venv
.venv\Scripts\activate   # Windows
# ou
source .venv/bin/activate   # Linux/Mac

# 2. Instalar TODAS as dependências
pip install -r requirements.txt

# 3. Configurar .env (copie exemplo abaixo)
code .env

# 4. Rodar migrações
make migrate
make migrate-agentic

# 5. PRONTO! Testar:
make ui
# Abre: http://localhost:8000/ui
```

---

## 📋 **Checklist de Setup**

### **✅ Passo 1: Python & Venv**

```bash
# Verificar Python
python --version
# Deve ser: Python 3.11+ (3.13 OK)

# Criar venv (se não tiver)
python -m venv .venv

# Ativar
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
```

---

### **✅ Passo 2: Dependências**

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar TUDO
pip install -r requirements.txt
```

**Pacotes principais instalados:**
- `openai` - LLM client
- `requests` - HTTP
- `sqlalchemy` - ORM
- `pymysql` - MySQL driver
- `fastapi`, `uvicorn` - API
- `trafilatura`, `beautifulsoup4`, `lxml` - **HTML extraction (NEW!)**
- `pydantic`, `pydantic-settings` - Schemas
- `structlog` - Logging
- `tiktoken` - Tokenização
- `pytest` - Testes

---

### **✅ Passo 3: Arquivo .env**

Crie `.env` na raiz do projeto:

```bash
# ============================================================================
# IMPORTANTE: Espaços ANTES de comentários inline!
# ERRADO: VALUE=30# comentário
# CERTO:  VALUE=30  # comentário
# ============================================================================

# OpenAI API
OPENAI_API_KEY=sk-your-api-key-here

# Google Custom Search Engine
GOOGLE_CSE_API_KEY=your-cse-api-key
GOOGLE_CSE_CX=your-search-engine-id

# MySQL Database (⚠️ Use MYSQL_DB, não MYSQL_DATABASE!)
MYSQL_HOST=your-mysql-host.mysql.database.azure.com
MYSQL_PORT=3306
MYSQL_USER=your-username
MYSQL_PASSWORD=your-password
MYSQL_DB=reg_cache
MYSQL_SSL_CA=/path/to/DigiCertGlobalRootCA.crt.pem

# Application Settings
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=30  # ⚠️ ESPAÇO antes do #!
TTL_DAYS=7

# Qdrant Vector Database (opcional)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
```

**Validar .env:**
```bash
python -c "from common.settings import settings; print('✅ Settings OK:', settings.mysql_db)"
```

---

### **✅ Passo 4: Database Setup**

```bash
# Criar schema inicial
make db-init

# Rodar migração de typing
make migrate

# Rodar migração agentic
make migrate-agentic
```

**Validar DB:**
```bash
python -c "from db.session import DatabaseSession; db=DatabaseSession(); print('✅ DB OK')"
```

---

### **✅ Passo 5: Testar Componentes**

```bash
# Testar LLM
python -c "from agentic.llm import LLMClient; from common.settings import settings; llm=LLMClient(settings.openai_api_key); print('✅ LLM OK')"

# Testar CSE
python -c "from agentic.cse_client import CSEClient; from common.env_readers import load_yaml_with_env; cfg=load_yaml_with_env('configs/cse.yaml'); cse=CSEClient(cfg['api_key'], cfg['cx'], 30); print('✅ CSE OK')"

# Rodar testes
pytest tests/test_agentic_*.py -v
```

---

## 🚀 **Primeira Execução**

### **Opção 1: Web UI (Visual)**

```bash
make ui

# Browser abre em: http://localhost:8000/ui
# Clique "📋 Exemplo"
# Clique "🧠 Gerar Plano"
# Clique "🚀 Executar"
```

### **Opção 2: CLI (Terminal)**

```bash
# Dry-run (sem API calls)
python scripts/run_agentic.py --prompt "Buscar RNs ANS" --dry-run

# Executar de verdade
python scripts/run_agentic.py \
  --plan-file examples/agentic_plan_permissive.json \
  --debug
```

### **Opção 3: VSCode (Debug)**

```
F5 → "🌐 Web UI + API (Debug Server)"
```

---

## 🐛 **Troubleshooting**

### **Erro: "No module named 'trafilatura'"**
```bash
✅ SOLUÇÃO: pip install -r requirements.txt
```

### **Erro: "MYSQL_DATABASE Field required"**
```bash
✅ SOLUÇÃO: No .env, use MYSQL_DB (não MYSQL_DATABASE)
```

### **Erro: "Timeout value connect was X#..."**
```bash
✅ SOLUÇÃO: Adicione ESPAÇO antes do # no .env
# ERRADO: REQUEST_TIMEOUT_SECONDS=30# comentário
# CERTO:  REQUEST_TIMEOUT_SECONDS=30  # comentário
```

### **Erro: "Unknown column 'final_type'"**
```bash
✅ SOLUÇÃO: Rodar migrações
make migrate
make migrate-agentic
```

### **Erro: "401 Unauthorized" (OpenAI)**
```bash
✅ SOLUÇÃO: Verificar OPENAI_API_KEY no .env
python -c "from common.settings import settings; print(settings.openai_api_key[:10])"
```

### **Erro: "CSE quota exceeded"**
```bash
✅ SOLUÇÃO: Google CSE free tier = 100 queries/dia
- Espere reset (meia-noite PST)
- Ou use dry-run: --dry-run
```

---

## 📦 **Estrutura de Pastas Esperada**

```
agentic-reg-ingest/
├── .env                    ← Suas credenciais (CRIE ESTE!)
├── .venv/                  ← Virtual environment
├── agentic/                ← Core modules
├── apps/
│   ├── api/
│   │   └── main.py         ← API + endpoints
│   └── ui/
│       └── static/
│           └── index.html  ← Web UI
├── configs/                ← YAMLs de config
├── db/
│   └── migrations/         ← SQL migrations
├── examples/               ← Planos prontos
├── pipelines/              ← Search, Ingest, Agentic
├── scripts/                ← CLI runners
├── tests/                  ← Test suite
├── requirements.txt        ← Dependências
└── Makefile                ← Comandos
```

---

## 🎯 **Ordem de Execução (primeira vez)**

```bash
# 1. Setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Config
# Crie .env com credenciais

# 3. Database
make db-init
make migrate
make migrate-agentic

# 4. Validar
pytest tests/test_agentic_plan.py -v

# 5. Executar!
make ui
# ou
python scripts/run_agentic.py --dry-run
```

---

## 🧪 **Validação Completa (Passo a Passo)**

```bash
# 1. Verificar Python
python --version
# ✅ Esperado: Python 3.11.x ou 3.13.x

# 2. Verificar venv
which python   # Linux/Mac
where python   # Windows
# ✅ Esperado: caminho dentro de .venv/

# 3. Verificar dependências
pip list | grep trafilatura
# ✅ Esperado: trafilatura 1.12.2 (ou 2.x)

# 4. Verificar .env
python -c "from common.settings import settings; print(settings.mysql_db)"
# ✅ Esperado: nome do seu DB (ex: reg_cache)

# 5. Verificar DB connection
python -c "from db.session import DatabaseSession; db=DatabaseSession(); print('OK')"
# ✅ Esperado: OK

# 6. Verificar tabelas
make migrate
make migrate-agentic
# ✅ Esperado: Migration complete.

# 7. Rodar dry-run
python scripts/run_agentic.py --prompt "Test" --dry-run
# ✅ Esperado: Mostra plano simulado

# 8. Rodar testes
pytest tests/test_agentic_plan.py -v
# ✅ Esperado: All tests passed

# 9. Iniciar UI
make ui
# ✅ Esperado: Uvicorn running on http://127.0.0.1:8000

# 10. Abrir browser
http://localhost:8000/ui
# ✅ Esperado: UI carrega
```

Se **TODOS** os passos passarem → **SISTEMA 100% OPERACIONAL!** 🎉

---

## 🎁 **Atalhos no requirements.txt**

Se quiser instalar só as novas deps HTML:

```bash
pip install trafilatura beautifulsoup4 lxml
```

Mas é **melhor** sempre rodar:
```bash
pip install -r requirements.txt
```

Para garantir versões consistentes.

---

## 🌟 **Primeira vez? Use este script:**

```bash
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edite depois!
make db-init
make migrate
make migrate-agentic
pytest tests/test_agentic_plan.py -v
make ui

# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edite depois!
make db-init
make migrate
make migrate-agentic
pytest tests/test_agentic_plan.py -v
make ui
```

---

**SETUP COMPLETO! AGORA RODE `make ui` E APROVEITE! 🚀🌐**


````

## [19] START_HERE.md

````markdown
# FILE: START_HERE.md
# FULL: C:\Projetos\agentic-reg-ingest\START_HERE.md
# NOTE: Concatenated snapshot for review
# 🚀 COMEÇAR AQUI - Guia Rápido de Execução

## ✅ Status Atual
- ✅ Virtual environment criado
- ✅ Dependências instaladas
- ✅ Arquivo .env existe

## 📝 PASSO A PASSO PARA RODAR AGORA

### PASSO 1: Configurar .env com suas credenciais
```powershell
# Abrir .env no VSCode
code .env
```

**Você PRECISA configurar estas variáveis:**
```env
GOOGLE_API_KEY=sua-chave-google-aqui       # Obtenha em: https://console.cloud.google.com/
GOOGLE_CX=seu-custom-search-id             # Configure em: https://programmablesearchengine.google.com/
OPENAI_API_KEY=sk-sua-chave-openai         # Obtenha em: https://platform.openai.com/api-keys

# Para o MySQL local, pode manter assim:
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=reg_cache
MYSQL_USER=root
MYSQL_PASSWORD=root
```

### PASSO 2: Subir MySQL via Docker
```powershell
# Iniciar MySQL
docker compose up -d mysql

# Verificar status (aguarde ficar "healthy")
docker compose ps

# Ver logs se necessário
docker compose logs -f mysql
```

**Aguarde ~15 segundos** para o MySQL inicializar completamente.

### PASSO 3: Criar tabelas no banco
```powershell
# Opção fácil
python -c "from db.session import init_db; from common.env_readers import load_yaml_with_env; init_db(load_yaml_with_env('configs/db.yaml'))"

# OU via Makefile (se funcionar no Windows)
make db-init
```

### PASSO 4: Rodar a Search Pipeline!

**Opção A: Via Python diretamente**
```powershell
python pipelines/search_pipeline.py --config configs/cse.yaml --db configs/db.yaml --query "RN 259 ANS" --topn 10
```

**Opção B: Via Debug no VSCode/Cursor** (RECOMENDADO)
1. Abra `pipelines/search_pipeline.py`
2. Coloque um breakpoint na linha ~87 (função `execute`)
3. Pressione `F5`
4. Selecione: **"Debug: Search Pipeline"**
5. Observe a execução!

**Opção C: Via Makefile**
```powershell
make search
```

## 🎯 Testando sem Google API (se não tiver ainda)

Se você ainda não tem as credenciais do Google, pode testar rodando os **testes**:

```powershell
# Rodar testes
pytest tests/test_scoring.py -v

# Ou todos
pytest tests/ -v
```

## 🌐 Testar API FastAPI

```powershell
# Subir servidor
uvicorn apps.api.main:app --reload --port 8000

# OU via debug
# F5 → Selecione "Debug: FastAPI Server"

# Acessar no navegador
# http://localhost:8000
# http://localhost:8000/docs  (Swagger UI)
```

## 🔍 Verificar se tudo está OK

```powershell
# Teste rápido de imports
python -c "from agentic.cse_client import CSEClient; from db.models import SearchQuery; print('✅ Imports OK!')"

# Ver se .env está sendo lido
python -c "from common.settings import settings; print(f'Google API: {settings.google_api_key[:10]}...')"
```

## ❌ Problemas Comuns

### "ModuleNotFoundError"
```powershell
# Certifique-se que o venv está ativo
.venv\Scripts\activate

# Reinstale
pip install -r requirements.txt
```

### "Can't connect to MySQL"
```powershell
# Reiniciar MySQL
docker compose restart mysql

# Aguardar 10 segundos
Start-Sleep -Seconds 10

# Testar conexão
docker compose exec mysql mysql -u root -proot -e "SELECT 1;"
```

### "ValidationError: GOOGLE_API_KEY"
```
Você precisa configurar o .env!
Abra o arquivo e preencha as credenciais.
```

## 🎓 Próximos Passos

Depois que a search pipeline funcionar:

1. **Ingest Pipeline:**
   ```powershell
   python pipelines/ingest_pipeline.py --config configs/ingest.yaml --db configs/db.yaml --limit 5
   ```

2. **Explorar Database:**
   ```powershell
   docker compose exec mysql mysql -u root -proot reg_cache
   # SQL: SELECT * FROM search_query;
   ```

3. **Ler os guias:**
   - `DEBUG_GUIDE.md` - Debug detalhado
   - `QUICK_REFERENCE.md` - Comandos úteis
   - `README.md` - Documentação completa

---

**Você está pronto! 🚀**

Qualquer dúvida, consulte os arquivos de documentação ou abra uma issue.


````

## [20] TEST_AGENTIC.md

````markdown
# FILE: TEST_AGENTIC.md
# FULL: C:\Projetos\agentic-reg-ingest\TEST_AGENTIC.md
# NOTE: Concatenated snapshot for review
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


````

## [21] agentic/__init__.py

```python
# FILE: agentic/__init__.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\__init__.py
# NOTE: Concatenated snapshot for review
"""Agentic modules for search and analysis."""


```

## [22] agentic/cse_client.py

```python
# FILE: agentic/cse_client.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\cse_client.py
# NOTE: Concatenated snapshot for review
"""Google Custom Search Engine (CSE) client."""

from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


class CSEClient:
    """Client for Google Programmable Search Engine API."""
    
    def __init__(self, api_key: str, cx: str, timeout: int = 30):
        """
        Initialize CSE client.
        
        Args:
            api_key: Google API key
            cx: Custom Search Engine ID
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.cx = cx
        self.timeout = timeout
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def search(
        self,
        query: str,
        start: int = 1,
        num: int = 10,
        language: str = "lang_pt",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute search query.
        
        Args:
            query: Search query string
            start: Start index (1-based)
            num: Number of results per page (max 10)
            language: Language restriction
            **kwargs: Additional CSE API parameters
            
        Returns:
            API response dictionary
            
        Raises:
            requests.RequestException: On API errors
        """
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "start": start,
            "num": num,
            "lr": language,
            **kwargs,
        }
        
        response = requests.get(
            self.base_url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        
        return response.json()
    
    def search_all(
        self,
        query: str,
        max_results: int = 100,
        results_per_page: int = 10,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute paginated search to collect multiple results.
        
        Args:
            query: Search query string
            max_results: Maximum total results to retrieve
            results_per_page: Results per API call (max 10)
            **kwargs: Additional CSE API parameters
            
        Returns:
            List of search result items
        """
        all_items = []
        start = 1
        
        while len(all_items) < max_results:
            try:
                response = self.search(
                    query=query,
                    start=start,
                    num=min(results_per_page, 10),
                    **kwargs,
                )
                
                items = response.get("items", [])
                if not items:
                    break
                
                all_items.extend(items)
                
                # Check if more results available
                search_info = response.get("searchInformation", {})
                total_results = int(search_info.get("totalResults", 0))
                
                if len(all_items) >= total_results:
                    break
                
                start += len(items)
                
            except requests.RequestException:
                # Stop on error
                break
        
        return all_items[:max_results]


```

## [23] agentic/detect.py

```python
# FILE: agentic/detect.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\detect.py
# NOTE: Concatenated snapshot for review
"""Robust document type detection with magic bytes, headers, and URL analysis."""

import re
import structlog
from typing import Dict, Optional
from urllib.parse import urlparse

import requests

logger = structlog.get_logger()


def _url_ext(url: str) -> Optional[str]:
    """
    Extract file extension from URL path.
    
    Args:
        url: URL to analyze
        
    Returns:
        Extension without dot ('pdf', 'zip', 'html', 'htm') or None
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Remove query params and fragments
        path = path.split('?')[0].split('#')[0]
        
        # Get extension
        if '.' in path:
            ext = path.rsplit('.', 1)[1]
            # Known extensions
            if ext in ('pdf', 'zip', 'html', 'htm', 'csv', 'txt', 'xlsx', 'xls'):
                return ext
        
        return None
    except Exception:
        return None


def _sniff_magic(url: str, timeout: int = 20) -> Optional[bytes]:
    """
    Fetch first 8 bytes via Range GET to detect magic bytes.
    
    Args:
        url: URL to sniff
        timeout: Request timeout in seconds
        
    Returns:
        First 8 bytes or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RegulatoryBot/1.0)',
            'Range': 'bytes=0-7',
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        
        # Accept 200 (full response) or 206 (partial content)
        if response.status_code in (200, 206):
            # Read first 8 bytes
            chunk = next(response.iter_content(chunk_size=8), b'')
            response.close()
            return chunk[:8]
        
        return None
        
    except Exception as e:
        logger.debug("magic_sniff_failed", url=url, error=str(e))
        return None


def _detect_from_magic(magic: bytes) -> Optional[str]:
    """
    Detect file type from magic bytes.
    
    Args:
        magic: First bytes of file
        
    Returns:
        'pdf', 'zip', or None
    """
    if not magic or len(magic) < 4:
        return None
    
    # PDF: %PDF- (25 50 44 46 2D)
    if magic.startswith(b'%PDF-'):
        return 'pdf'
    
    # ZIP: PK signatures
    # PK\x03\x04 (normal zip)
    # PK\x05\x06 (empty zip)
    # PK\x07\x08 (spanned zip)
    if magic.startswith(b'PK\x03\x04') or \
       magic.startswith(b'PK\x05\x06') or \
       magic.startswith(b'PK\x07\x08'):
        return 'zip'
    
    return None


def _detect_from_disposition(disposition: Optional[str]) -> Optional[str]:
    """
    Detect file type from Content-Disposition filename.
    
    Args:
        disposition: Content-Disposition header value
        
    Returns:
        'pdf', 'zip', 'html', or None
    """
    if not disposition:
        return None
    
    # Extract filename from Content-Disposition
    # Example: attachment; filename="document.pdf"
    # Example: inline; filename*=UTF-8''file%20name.zip
    
    filename_match = re.search(r'filename[*]?=["\']?([^"\';\s]+)', disposition, re.IGNORECASE)
    if filename_match:
        filename = filename_match.group(1).lower()
        
        # Decode URL-encoded filenames
        try:
            from urllib.parse import unquote
            filename = unquote(filename)
        except Exception:
            pass
        
        # Check extension
        if filename.endswith('.pdf'):
            return 'pdf'
        elif filename.endswith('.zip'):
            return 'zip'
        elif filename.endswith(('.html', '.htm')):
            return 'html'
    
    return None


def _detect_from_content_type(content_type: Optional[str], url_extension: Optional[str]) -> Optional[str]:
    """
    Detect file type from Content-Type header.
    
    Args:
        content_type: Content-Type header value
        url_extension: URL extension for disambiguation
        
    Returns:
        'pdf', 'zip', 'html', or None
    """
    if not content_type:
        return None
    
    content_type_lower = content_type.lower()
    
    # PDF
    if 'pdf' in content_type_lower or 'application/pdf' in content_type_lower:
        return 'pdf'
    
    # ZIP
    if 'zip' in content_type_lower or \
       'application/zip' in content_type_lower or \
       'application/x-zip-compressed' in content_type_lower:
        return 'zip'
    
    # HTML
    if 'html' in content_type_lower or 'text/html' in content_type_lower:
        # But check URL extension - if URL says .pdf, trust that over Content-Type
        if url_extension == 'pdf':
            return 'pdf'
        elif url_extension == 'zip':
            return 'zip'
        return 'html'
    
    # Text (could be HTML without proper MIME)
    if 'text/' in content_type_lower:
        # Check URL extension for clarification
        if url_extension in ('html', 'htm'):
            return 'html'
        elif url_extension == 'pdf':
            return 'pdf'
        # Default text to HTML
        return 'html'
    
    return None


def detect_type(url: str, head_headers: Dict[str, str], sniff_magic: bool = True) -> Dict[str, Optional[str]]:
    """
    Detect document type using multiple signals.
    
    Detection order (first match wins):
    1. Magic bytes (if sniff_magic=True)
    2. Content-Disposition filename
    3. Content-Type header (with URL extension disambiguation)
    4. URL extension
    5. Fallback: 'unknown'
    
    Args:
        url: Document URL
        head_headers: Headers from HEAD request (dict with Content-Type, Content-Disposition, etc.)
        sniff_magic: Whether to fetch magic bytes via Range GET
        
    Returns:
        Dictionary with:
        - detected_mime: MIME type from headers or magic
        - detected_ext: Extension from detection
        - final_type: 'pdf' | 'zip' | 'html' | 'unknown'
        - fetch_status: 'ok' | 'redirected' | 'blocked' | 'error'
    """
    result = {
        "detected_mime": None,
        "detected_ext": None,
        "final_type": "unknown",
        "fetch_status": "ok",
    }
    
    # Extract signals
    content_type = head_headers.get('Content-Type') or head_headers.get('content-type')
    content_disposition = head_headers.get('Content-Disposition') or head_headers.get('content-disposition')
    url_extension = _url_ext(url)
    
    detected_type = None
    detection_source = None
    
    try:
        # 1. Magic bytes (highest priority)
        if sniff_magic:
            magic = _sniff_magic(url)
            if magic:
                magic_type = _detect_from_magic(magic)
                if magic_type:
                    detected_type = magic_type
                    detection_source = "magic"
                    result["detected_mime"] = f"application/{magic_type}" if magic_type in ('pdf', 'zip') else None
                    result["detected_ext"] = magic_type
        
        # 2. Content-Disposition filename
        if not detected_type:
            disp_type = _detect_from_disposition(content_disposition)
            if disp_type:
                detected_type = disp_type
                detection_source = "disposition"
                result["detected_ext"] = disp_type
        
        # 3. Content-Type header
        if not detected_type:
            ctype_result = _detect_from_content_type(content_type, url_extension)
            if ctype_result:
                detected_type = ctype_result
                detection_source = "content_type"
                result["detected_mime"] = content_type
        
        # 4. URL extension
        if not detected_type and url_extension:
            if url_extension in ('pdf', 'zip'):
                detected_type = url_extension
                detection_source = "url_ext"
                result["detected_ext"] = url_extension
            elif url_extension in ('html', 'htm'):
                detected_type = 'html'
                detection_source = "url_ext"
                result["detected_ext"] = url_extension
        
        # Set final type
        if detected_type:
            result["final_type"] = detected_type
            logger.debug(
                "type_detected",
                url=url,
                final_type=detected_type,
                source=detection_source,
            )
        else:
            result["final_type"] = "unknown"
            logger.debug("type_unknown", url=url)
        
    except Exception as e:
        logger.error("detection_error", url=url, error=str(e))
        result["fetch_status"] = "error"
    
    return result


```

## [24] agentic/html_extract.py

```python
# FILE: agentic/html_extract.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\html_extract.py
# NOTE: Concatenated snapshot for review
"""HTML extraction utilities with readability and PDF wrapper detection."""

import re
import structlog
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import trafilatura
from bs4 import BeautifulSoup

logger = structlog.get_logger()


def clean_html_to_excerpt(html: str, base_url: str, max_chars: int) -> Dict:
    """
    Extract clean text excerpt from HTML with anchors and PDF links.
    
    Args:
        html: Raw HTML content
        base_url: Base URL for resolving relative links
        max_chars: Maximum characters to return
        
    Returns:
        Dictionary with:
        - excerpt: Clean text content
        - pdf_links: List of absolute PDF URLs found
        - anchors_struct: List of heading/table anchors
    """
    result = {
        "excerpt": "",
        "pdf_links": [],
        "anchors_struct": [],
    }
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script, style, noscript tags
        for tag in soup(['script', 'style', 'noscript', 'meta', 'link']):
            tag.decompose()
        
        # Collect PDF links
        pdf_links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # Check if likely PDF
            if href.lower().endswith('.pdf') or '.pdf?' in href.lower():
                pdf_links.add(absolute_url)
            elif 'pdf' in href.lower() and urlparse(href).path.endswith('.pdf'):
                pdf_links.add(absolute_url)
        
        result["pdf_links"] = sorted(list(pdf_links))
        
        # Collect heading anchors
        anchors = []
        for level in range(1, 5):  # h1, h2, h3, h4
            for heading in soup.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                if text:
                    anchors.append({
                        "type": f"h{level}",
                        "value": text[:200],  # Truncate very long headings
                    })
        
        # Collect table markers
        for table in soup.find_all('table'):
            # Try to find caption or first row header
            caption = table.find('caption')
            if caption:
                caption_text = caption.get_text(strip=True)
            else:
                # Try first row
                first_row = table.find('tr')
                if first_row:
                    headers = first_row.find_all(['th', 'td'])
                    caption_text = ' | '.join([h.get_text(strip=True) for h in headers[:3]])
                else:
                    caption_text = "Table"
            
            if caption_text:
                anchors.append({
                    "type": "table",
                    "value": caption_text[:200],
                })
        
        result["anchors_struct"] = anchors
        
        # Extract clean text using trafilatura
        try:
            # Try trafilatura first (best for article extraction)
            extracted = trafilatura.extract(
                html,
                output_format='xml',
                include_tables=True,
                include_links=False,
                include_images=False,
            )
            
            if extracted:
                # Parse XML output to get text
                xml_soup = BeautifulSoup(extracted, 'lxml-xml')
                text = xml_soup.get_text(separator='\n', strip=True)
            else:
                # Fallback to soup
                text = soup.get_text(separator='\n', strip=True)
        
        except Exception as e:
            logger.warning("trafilatura_failed", error=str(e))
            # Fallback to BeautifulSoup
            text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines -> double
        text = re.sub(r' +', ' ', text)  # Multiple spaces -> single
        
        # Truncate to max_chars
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        result["excerpt"] = text
        
        logger.debug(
            "html_excerpt_extracted",
            url=base_url,
            excerpt_len=len(text),
            pdf_links_count=len(pdf_links),
            anchors_count=len(anchors),
        )
        
    except Exception as e:
        logger.error("html_extract_failed", url=base_url, error=str(e))
        result["excerpt"] = html[:max_chars] if html else ""
    
    return result


def is_probably_pdf_wrapper(html: str, base_url: str) -> Optional[str]:
    """
    Detect if HTML is a PDF wrapper/redirect page.
    
    Args:
        html: Raw HTML content
        base_url: Base URL
        
    Returns:
        Absolute URL of PDF if detected, else None
    """
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Check for iframe/embed pointing to PDF
        for tag in soup.find_all(['iframe', 'embed', 'object']):
            src = tag.get('src') or tag.get('data')
            if src:
                absolute_url = urljoin(base_url, src)
                if src.lower().endswith('.pdf') or '.pdf?' in src.lower():
                    logger.info("pdf_wrapper_iframe_detected", url=base_url, pdf=absolute_url)
                    return absolute_url
        
        # Check for meta refresh to PDF
        for meta in soup.find_all('meta', attrs={'http-equiv': re.compile('refresh', re.I)}):
            content = meta.get('content', '')
            # Format: "0;URL=http://example.com/file.pdf"
            match = re.search(r'url\s*=\s*["\']?([^"\'>\s]+)', content, re.I)
            if match:
                url = match.group(1)
                absolute_url = urljoin(base_url, url)
                if url.lower().endswith('.pdf') or '.pdf?' in url.lower():
                    logger.info("pdf_wrapper_meta_detected", url=base_url, pdf=absolute_url)
                    return absolute_url
        
        # Check for dominant PDF link (main content is just a download link)
        body_text = soup.body.get_text(strip=True) if soup.body else ""
        if len(body_text) < 500:  # Very short page
            # Look for prominent PDF link
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf') or '.pdf?' in href.lower():
                    link_text = link.get_text(strip=True).lower()
                    # Keywords indicating it's a download page
                    if any(kw in link_text for kw in ['download', 'baixar', 'pdf', 'documento', 'arquivo']):
                        absolute_url = urljoin(base_url, href)
                        logger.info("pdf_wrapper_link_detected", url=base_url, pdf=absolute_url)
                        return absolute_url
        
        return None
        
    except Exception as e:
        logger.error("pdf_wrapper_detection_failed", url=base_url, error=str(e))
        return None


```

## [25] agentic/llm.py

```python
# FILE: agentic/llm.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\llm.py
# NOTE: Concatenated snapshot for review
"""LLM wrapper for intelligent routing and PDF analysis."""

import json
import structlog
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from agentic.schemas import CandidateSummary, JudgeResponse, Plan

logger = structlog.get_logger()


class LLMClient:
    """OpenAI LLM client for agentic tasks."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        max_tokens: int = 2000,
        timeout: int = 30,
    ):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenAI API key
            model: Model name
            temperature: Sampling temperature
            max_tokens: Max response tokens
            timeout: Request timeout
        """
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def _call_chat_completion(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Call OpenAI chat completion API.
        
        Args:
            messages: List of chat messages
            response_format: Optional response format spec
            
        Returns:
            Response content string
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
    
    def suggest_pdf_markers(
        self,
        title: str,
        pages_preview: List[str],
        domain: str,
    ) -> List[Dict[str, Any]]:
        """
        Suggest anchoring markers for PDF chunking.
        
        Args:
            title: Document title
            pages_preview: Preview text from first few pages
            domain: Source domain
            
        Returns:
            List of marker suggestions with type and patterns
            Example: [
                {"type": "article", "pattern": "Art\\. \\d+"},
                {"type": "chapter", "pattern": "CAPÍTULO [IVX]+"},
                {"type": "annex", "pattern": "ANEXO [IVX]+"},
            ]
        """
        preview_text = "\n---\n".join(pages_preview[:5])
        
        prompt = f"""You are analyzing a regulatory document from {domain}.

Title: {title}

First pages preview:
{preview_text}

Suggest anchoring markers to guide intelligent chunking. Return a JSON array of markers.

Each marker should have:
- "type": one of "article", "chapter", "section", "annex", "table", "page_range"
- "pattern": regex pattern to detect this marker
- "confidence": 0.0-1.0

Example:
[
  {{"type": "article", "pattern": "Art\\\\. \\\\d+", "confidence": 0.9}},
  {{"type": "annex", "pattern": "ANEXO [IVX]+", "confidence": 0.8}}
]

Return only valid JSON array, no explanation."""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that returns valid JSON."},
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = self._call_chat_completion(
                messages,
                response_format={"type": "json_object"},
            )
            
            # OpenAI json_object mode wraps array in object, extract it
            parsed = json.loads(response)
            
            # Handle different response structures
            if isinstance(parsed, list):
                markers = parsed
            elif "markers" in parsed:
                markers = parsed["markers"]
            elif "suggestions" in parsed:
                markers = parsed["suggestions"]
            else:
                # Fallback: use first list found
                for value in parsed.values():
                    if isinstance(value, list):
                        markers = value
                        break
                else:
                    markers = []
            
            return markers
        
        except Exception:
            # Fallback to default markers
            return [
                {"type": "article", "pattern": r"Art\. \d+", "confidence": 0.5},
                {"type": "chapter", "pattern": r"CAP[ÍI]TULO [IVX]+", "confidence": 0.5},
            ]
    
    def route_fallback(
        self,
        title: str,
        snippet: str,
        url: str,
    ) -> Literal["pdf", "zip", "html"]:
        """
        Fallback routing when content-type is ambiguous.
        
        Args:
            title: Document title
            snippet: Search snippet
            url: Document URL
            
        Returns:
            Document type: 'pdf', 'zip', or 'html'
        """
        prompt = f"""Based on the following information, determine the document type.

Title: {title}
Snippet: {snippet}
URL: {url}

Return ONLY one word: "pdf", "zip", or "html"."""
        
        messages = [
            {"role": "system", "content": "You return only one word: pdf, zip, or html."},
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = self._call_chat_completion(messages)
            response_lower = response.strip().lower()
            
            if "pdf" in response_lower:
                return "pdf"
            elif "zip" in response_lower:
                return "zip"
            else:
                return "html"
        
        except Exception:
            # Default fallback
            if url.lower().endswith('.pdf'):
                return "pdf"
            elif url.lower().endswith('.zip'):
                return "zip"
            else:
                return "html"
    
    def extract_html_structure(
        self,
        base_url: str,
        excerpt: str,
        max_chars_llm: int = 80000,
    ) -> Dict[str, Any]:
        """
        Extract structure from HTML content using LLM.
        
        This does NOT summarize - it STRUCTURES the content by identifying
        sections, headings, tables, and anchors for intelligent chunking.
        
        Args:
            base_url: Source URL
            excerpt: HTML text excerpt (already cleaned)
            max_chars_llm: Maximum characters to send to LLM
            
        Returns:
            Dictionary with:
            {
                "title": str | null,
                "language": "pt" | "en" | ...,
                "sections": [{"heading": str, "text": str}],
                "tables": [{"caption": str, "rows": int | null}],
                "pdf_links": [str],
                "anchors": [{"type": "h1|h2|h3|h4|table|page", "value": str, "hint": str | null}]
            }
        """
        # Truncate excerpt if too long
        if len(excerpt) > max_chars_llm:
            excerpt = excerpt[:max_chars_llm] + "\n\n[...truncated...]"
        
        system_prompt = """Você extrai estrutura de documentos HTML regulatórios (ANS/Planalto/ANPD/BACEN/CVM).

IMPORTANTE:
- Responda APENAS com JSON válido
- NÃO resuma o conteúdo - preserve seções na ordem original
- NÃO invente links ou informações
- Use o schema exato especificado

Campos obrigatórios:
{
  "title": string ou null,
  "language": "pt" | "en" | "es" | "other",
  "sections": [{"heading": string, "text": string}],
  "tables": [{"caption": string, "rows": number ou null}],
  "pdf_links": [string],
  "anchors": [{"type": "h1|h2|h3|h4|table|page", "value": string, "hint": string ou null}]
}

Regras:
- 'sections' preserva a ordem do texto principal com headings
- 'anchors' lista h1..h4 e 'table' com nomes/títulos aparentes
- Use 'page' em anchors apenas se não houver headings
- Evite repetir conteúdo entre seções
- Nunca invente links ou dados"""

        user_prompt = json.dumps({
            "base_url": base_url,
            "html_excerpt": excerpt,
        }, ensure_ascii=False)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        try:
            logger.info("llm_html_struct_start", url=base_url, excerpt_len=len(excerpt))
            
            response = self._call_chat_completion(
                messages,
                response_format={"type": "json_object"},
            )
            
            structure = json.loads(response)
            
            # Validate and fill missing fields
            result = {
                "title": structure.get("title"),
                "language": structure.get("language", "pt"),
                "sections": structure.get("sections", []),
                "tables": structure.get("tables", []),
                "pdf_links": structure.get("pdf_links", []),
                "anchors": structure.get("anchors", []),
            }
            
            logger.info(
                "llm_html_struct_done",
                url=base_url,
                sections_count=len(result["sections"]),
                tables_count=len(result["tables"]),
                anchors_count=len(result["anchors"]),
            )
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error("llm_html_struct_json_error", url=base_url, error=str(e))
            # Return minimal schema
            return {
                "title": None,
                "language": "pt",
                "sections": [],
                "tables": [],
                "pdf_links": [],
                "anchors": [],
            }
        
        except Exception as e:
            logger.error("llm_html_struct_failed", url=base_url, error=str(e))
            # Return minimal schema
            return {
                "title": None,
                "language": "pt",
                "sections": [],
                "tables": [],
                "pdf_links": [],
                "anchors": [],
            }
    
    def plan_from_prompt(self, user_prompt: str) -> "Plan":
        """
        Generate agentic search plan from natural language prompt.
        
        Args:
            user_prompt: User's search goal in natural language
            
        Returns:
            Validated Plan object
        """
        system_prompt = """Você é um planejador de busca regulatória em saúde suplementar (ANS/Planalto/ANPD/BACEN/CVM).

IMPORTANTE:
- Gere um PLANO JSON estrito – nada de prosa
- Objetivo: maximizar fontes oficiais citáveis (PDF/ZIP) e minimizar ruído
- Inclua queries (com 'k'), allowlist, stop conditions e quality gates
- Use linguagem portuguesa para termos, mas os campos JSON em inglês

Schema obrigatório:
{
  "goal": string (objetivo da busca),
  "topics": [string] (tópicos principais),
  "queries": [{"q": string, "why": string|null, "k": int (1-10)}],
  "allow_domains": [string] (ex: ["www.gov.br", "www.planalto.gov.br"]),
  "deny_patterns": [string] (regex patterns para excluir),
  "stop": {
    "min_approved": int (mínimo de documentos aprovados),
    "max_iterations": int (máximo de iterações),
    "max_queries_per_iter": int (queries por iteração)
  },
  "quality_gates": {
    "must_types": [string] (ex: ["pdf","zip"]),
    "max_age_years": int,
    "min_anchor_signals": int,
    "min_score": float (0.0-1.0)
  },
  "budget": {
    "max_cse_calls": int,
    "ttl_days": int
  }
}

Dicas:
- Para ANS: use "www.gov.br/ans" no allowlist
- Para Planalto: use "www.planalto.gov.br"
- Queries devem ser específicas (ex: "RN 395 ANS", "Resolução Normativa")
- k entre 5-10 por query
- must_types geralmente ["pdf","zip"] para documentos oficiais"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        try:
            logger.info("llm_plan_start", prompt_len=len(user_prompt))
            
            response = self._call_chat_completion(
                messages,
                response_format={"type": "json_object"},
            )
            
            plan_dict = json.loads(response)
            
            # Import here to avoid circular dependency
            from agentic.schemas import Plan
            
            # Validate and construct Plan
            plan = Plan(**plan_dict)
            
            logger.info(
                "llm_plan_done",
                queries_count=len(plan.queries),
                min_approved=plan.stop.min_approved,
                must_types=plan.quality_gates.must_types,
            )
            
            return plan
        
        except json.JSONDecodeError as e:
            logger.error("llm_plan_json_error", error=str(e))
            raise ValueError(f"Failed to parse plan JSON: {e}")
        
        except Exception as e:
            logger.error("llm_plan_failed", error=str(e))
            raise
    
    def judge_candidates(
        self,
        plan: "Plan",
        candidates: List["CandidateSummary"],
    ) -> "JudgeResponse":
        """
        Judge search candidates and propose new queries.
        
        Args:
            plan: Search plan with quality gates
            candidates: List of candidate summaries to judge
            
        Returns:
            JudgeResponse with approved_urls, rejected, and new_queries
        """
        system_prompt = """Você é um crítico rigoroso de fontes regulatórias.

TAREFA:
Recebe candidatos (título/url/snippet/headers/score/final_type/anchor_signals) e um Plan (quality_gates).
Devolva JSON estrito com:
{
  "approved_urls": [string],
  "rejected": [{"url": string, "reason": string, "violations": [string]}],
  "new_queries": [string]
}

CRITÉRIOS DE REJEIÇÃO:
- Wrappers HTML (páginas que só linkam para PDF)
- Blogs, notícias, ou fontes não-oficiais
- Documentos desatualizados
- Baixa relevância ao objetivo
- Falta de marcadores estruturais (Art., Anexo, Tabela)

SUGESTÕES DE QUERIES:
- Se faltam anexos específicos, sugira "Anexo X RN Y"
- Se faltam tabelas, sugira "Tabela TUSS" ou similar
- Se faltam resoluções, sugira "RN [número]"
- Máximo 3 novas queries por iteração

IMPORTANTE:
- Apenas URLs em approved_urls que realmente atendem aos quality_gates
- Seja conservador: na dúvida, rejeite
- Reasons devem ser específicas e em português"""

        # Prepare user content
        user_content = {
            "plan_goal": plan.goal,
            "quality_gates": {
                "must_types": plan.quality_gates.must_types,
                "max_age_years": plan.quality_gates.max_age_years,
                "min_anchor_signals": plan.quality_gates.min_anchor_signals,
                "min_score": plan.quality_gates.min_score,
            },
            "candidates": [
                {
                    "url": c.url,
                    "title": c.title,
                    "snippet": c.snippet,
                    "score": c.score,
                    "final_type": c.final_type,
                    "anchor_signals": c.anchor_signals,
                    "last_modified": c.headers.get("Last-Modified"),
                }
                for c in candidates
            ],
        }
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_content, ensure_ascii=False)},
        ]
        
        try:
            logger.info("llm_judge_start", candidates_count=len(candidates))
            
            response = self._call_chat_completion(
                messages,
                response_format={"type": "json_object"},
            )
            
            judge_dict = json.loads(response)
            
            # Import here to avoid circular dependency
            from agentic.schemas import JudgeResponse, RejectedSummary
            
            # Ensure rejected has proper structure
            rejected_list = []
            for r in judge_dict.get("rejected", []):
                if isinstance(r, dict):
                    rejected_list.append(RejectedSummary(**r))
                else:
                    # Fallback if LLM didn't follow schema
                    rejected_list.append(RejectedSummary(
                        url=str(r),
                        reason="Rejected by judge",
                        violations=[],
                    ))
            
            judge_response = JudgeResponse(
                approved_urls=judge_dict.get("approved_urls", []),
                rejected=rejected_list,
                new_queries=judge_dict.get("new_queries", []),
            )
            
            logger.info(
                "llm_judge_done",
                approved_count=len(judge_response.approved_urls),
                rejected_count=len(judge_response.rejected),
                new_queries_count=len(judge_response.new_queries),
            )
            
            return judge_response
        
        except json.JSONDecodeError as e:
            logger.error("llm_judge_json_error", error=str(e))
            # Return safe fallback
            from agentic.schemas import JudgeResponse
            return JudgeResponse(approved_urls=[], rejected=[], new_queries=[])
        
        except Exception as e:
            logger.error("llm_judge_failed", error=str(e))
            # Return safe fallback
            from agentic.schemas import JudgeResponse
            return JudgeResponse(approved_urls=[], rejected=[], new_queries=[])


```

## [26] agentic/normalize.py

```python
# FILE: agentic/normalize.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\normalize.py
# NOTE: Concatenated snapshot for review
"""URL normalization utilities."""

from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """
    Normalize URL to canonical form.
    
    - Remove fragments (#)
    - Remove trailing slashes
    - Lowercase scheme and netloc
    - Keep query parameters
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL
    """
    parsed = urlparse(url)
    
    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip('/') if parsed.path != '/' else parsed.path
    params = parsed.params
    query = parsed.query
    # Remove fragment
    fragment = ''
    
    normalized = urlunparse((scheme, netloc, path, params, query, fragment))
    return normalized


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain (netloc)
    """
    parsed = urlparse(url)
    return parsed.netloc.lower()


def is_gov_domain(domain: str) -> bool:
    """
    Check if domain is a government domain.
    
    Args:
        domain: Domain string
        
    Returns:
        True if government domain
    """
    gov_tlds = ['.gov.br', 'ans.gov.br', 'saude.gov.br', 'planalto.gov.br', 'in.gov.br']
    return any(domain.endswith(tld) for tld in gov_tlds)


```

## [27] agentic/quality.py

```python
# FILE: agentic/quality.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\quality.py
# NOTE: Concatenated snapshot for review
"""Quality gates for agentic search candidate filtering."""

import re
from datetime import datetime, timedelta
from typing import List, Tuple

from agentic.schemas import CandidateSummary, QualityGates


def apply_quality_gates(
    gates: QualityGates,
    candidate: CandidateSummary,
) -> Tuple[bool, List[str]]:
    """
    Apply quality gates to a candidate.
    
    Args:
        gates: Quality gate configuration
        candidate: Candidate to evaluate
        
    Returns:
        Tuple of (approved: bool, violations: List[str])
    """
    violations = []
    
    # Gate 1: Document type must be in allowed list
    if candidate.final_type not in gates.must_types:
        violations.append(f"type:not_allowed (got '{candidate.final_type}', want {gates.must_types})")
    
    # Gate 2: Age check via Last-Modified header
    last_modified_str = candidate.headers.get("Last-Modified")
    if last_modified_str and gates.max_age_years > 0:
        try:
            # Parse Last-Modified header
            last_modified = datetime.strptime(
                last_modified_str,
                "%a, %d %b %Y %H:%M:%S %Z"
            )
            age_years = (datetime.utcnow() - last_modified).days / 365.25
            
            if age_years > gates.max_age_years:
                violations.append(f"age:stale ({age_years:.1f} years > {gates.max_age_years} years)")
        
        except Exception:
            # Failed to parse date, treat as warning but not blocking
            pass
    
    # Gate 3: Score threshold
    if candidate.score < gates.min_score:
        violations.append(f"score:low ({candidate.score:.2f} < {gates.min_score:.2f})")
    
    # Gate 4: Anchor signals (structural markers)
    if candidate.anchor_signals < gates.min_anchor_signals:
        violations.append(f"anchors:insufficient ({candidate.anchor_signals} < {gates.min_anchor_signals})")
    
    approved = len(violations) == 0
    
    return approved, violations


def count_anchor_signals(text: str) -> int:
    """
    Count structural/anchor signals in text (title, snippet, etc).
    
    Looks for:
    - Art. / Artigo
    - Anexo / ANEXO
    - Tabela / Table
    - Capítulo / CAPÍTULO
    - Heading tags (h1, h2, h3)
    
    Args:
        text: Text to analyze
        
    Returns:
        Count of anchor signals found
    """
    if not text:
        return 0
    
    text_lower = text.lower()
    count = 0
    
    # Regulatory markers
    patterns = [
        r'\bart\.\s*\d+',           # Art. 1, Art. 123
        r'\bartigo\s+\d+',          # Artigo 1
        r'\banexo\s+[ivxlcdm\d]+',  # Anexo I, Anexo 1
        r'\btabela\s+\d+',          # Tabela 1
        r'\bcap[íi]tulo\s+[ivxlcdm\d]+',  # Capítulo I
        r'\bseção\s+[ivxlcdm\d]+',  # Seção I
        r'\bparágrafo\s+\d+',       # Parágrafo 1
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        count += len(matches)
    
    # HTML heading tags (if present in snippet)
    heading_patterns = [
        r'<h[1-3]>',
        r'\bh1\b',
        r'\bh2\b',
        r'\bh3\b',
    ]
    
    for pattern in heading_patterns:
        matches = re.findall(pattern, text_lower)
        count += len(matches)
    
    return count


```

## [28] agentic/schemas.py

```python
# FILE: agentic/schemas.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\schemas.py
# NOTE: Concatenated snapshot for review
"""Pydantic schemas for Agentic Search system."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class QuerySpec(BaseModel):
    """Single query specification."""
    q: str = Field(..., description="Query string")
    why: Optional[str] = Field(None, description="Rationale for this query")
    k: int = Field(10, ge=1, le=10, description="Desired results per query")


class StopConditions(BaseModel):
    """Loop termination conditions."""
    min_approved: int = Field(12, ge=1, description="Minimum approved documents to collect")
    max_iterations: int = Field(3, ge=1, le=10, description="Maximum loop iterations")
    max_queries_per_iter: int = Field(2, ge=1, le=5, description="Max queries to execute per iteration")


class QualityGates(BaseModel):
    """Quality criteria for candidate approval."""
    must_types: List[str] = Field(["pdf", "zip"], description="Allowed final_type values")
    max_age_years: int = Field(3, ge=0, description="Maximum document age in years")
    min_anchor_signals: int = Field(1, ge=0, description="Minimum anchor/structure signals")
    min_score: float = Field(0.65, ge=0.0, le=5.0, description="Minimum scoring threshold (0-5 scale)")


class Budget(BaseModel):
    """Resource budget constraints."""
    max_cse_calls: int = Field(60, ge=1, description="Maximum CSE API calls")
    ttl_days: int = Field(7, ge=1, description="Cache TTL in days")


class Plan(BaseModel):
    """Agentic search plan."""
    goal: str = Field(..., description="Search objective")
    topics: List[str] = Field(default_factory=list, description="Topic areas")
    queries: List[QuerySpec] = Field(..., min_items=1, description="Query specifications")
    allow_domains: List[str] = Field(default_factory=list, description="Whitelist domains")
    deny_patterns: List[str] = Field(default_factory=list, description="Blacklist regex patterns")
    stop: StopConditions = Field(default_factory=StopConditions, description="Stop conditions")
    quality_gates: QualityGates = Field(default_factory=QualityGates, description="Quality criteria")
    budget: Budget = Field(default_factory=Budget, description="Resource budget")


class CandidateSummary(BaseModel):
    """Summary of a search result candidate."""
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    headers: dict = Field(default_factory=dict, description="HTTP headers")
    score: float = Field(0.0, ge=0.0, le=5.0, description="Composite score (0-5, weighted sum)")
    final_type: str = Field("unknown", description="Detected document type")
    anchor_signals: int = Field(0, ge=0, description="Count of structural signals")


class RejectedSummary(BaseModel):
    """Summary of a rejected candidate."""
    url: str
    reason: str
    violations: List[str] = Field(default_factory=list, description="Quality gate violations")


class IterationResult(BaseModel):
    """Result of one agentic loop iteration."""
    iteration: int
    executed_queries: List[str]
    candidates: List[CandidateSummary]
    approved: List[CandidateSummary]
    rejected: List[RejectedSummary]
    new_queries: List[str]
    reason_to_continue: Optional[str] = None


class JudgeResponse(BaseModel):
    """LLM judge response."""
    approved_urls: List[str] = Field(default_factory=list)
    rejected: List[RejectedSummary] = Field(default_factory=list)
    new_queries: List[str] = Field(default_factory=list)


class AgenticResult(BaseModel):
    """Final result of agentic search."""
    plan_id: str
    iterations: int
    approved_total: int
    stopped_by: str = Field(..., description="Reason for stopping: min_approved|max_iterations|budget|no_progress")
    promoted_urls: List[str]
    summary: Optional[str] = None


```

## [29] agentic/scoring.py

```python
# FILE: agentic/scoring.py
# FULL: C:\Projetos\agentic-reg-ingest\agentic\scoring.py
# NOTE: Concatenated snapshot for review
"""Scoring and ranking for search results."""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from agentic.normalize import is_gov_domain


class ResultScorer:
    """Score search results based on multiple factors."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize scorer with configuration.
        
        Args:
            config: Configuration dict from cse.yaml
        """
        self.config = config
        self.authority_domains = config.get("authority_domains", [])
        self.specificity_keywords = config.get("specificity_keywords", {})
        self.type_preferences = config.get("type_preferences", {})
        self.anchor_markers = config.get("anchor_markers", [])
    
    def score(
        self,
        url: str,
        title: Optional[str],
        snippet: Optional[str],
        content_type: Optional[str],
        last_modified: Optional[datetime],
    ) -> float:
        """
        Compute composite score for a search result.
        
        Score components:
        - Authority (0.0-1.0): Government domains preferred
        - Freshness (0.0-1.0): Recent content preferred
        - Specificity (0.0-1.0): Regulatory keywords boost
        - Type boost (1.0-1.5): PDF > ZIP > HTML
        - Anchorability (0.0-0.2): Presence of structural markers
        
        Args:
            url: Document URL
            title: Document title
            snippet: Search snippet
            content_type: Content-Type header value
            last_modified: Last-Modified timestamp
            
        Returns:
            Composite score (0.0-5.0+)
        """
        authority = self._score_authority(url)
        freshness = self._score_freshness(last_modified)
        specificity = self._score_specificity(title, snippet, url)
        type_boost = self._score_type(content_type, url)
        anchorability = self._score_anchorability(snippet)
        
        # Weighted sum
        score = (
            authority * 1.0
            + freshness * 0.8
            + specificity * 1.2
            + type_boost
            + anchorability
        )
        
        return round(score, 4)
    
    def _score_authority(self, url: str) -> float:
        """Score based on domain authority."""
        domain = urlparse(url).netloc.lower()
        
        if is_gov_domain(domain):
            return 1.0
        
        # Check configured authority domains
        for auth_domain in self.authority_domains:
            if domain.endswith(auth_domain):
                return 1.0
        
        return 0.3
    
    def _score_freshness(self, last_modified: Optional[datetime]) -> float:
        """Score based on content freshness."""
        if not last_modified:
            return 0.5  # Unknown = medium score
        
        now = datetime.utcnow()
        age_days = (now - last_modified).days
        
        # Bucket by age
        if age_days < 30:
            return 1.0
        elif age_days < 90:
            return 0.9
        elif age_days < 180:
            return 0.8
        elif age_days < 365:
            return 0.6
        elif age_days < 730:
            return 0.4
        else:
            return 0.2
    
    def _score_specificity(
        self,
        title: Optional[str],
        snippet: Optional[str],
        url: str,
    ) -> float:
        """Score based on regulatory keyword presence."""
        text = " ".join(filter(None, [title or "", snippet or "", url]))
        text_lower = text.lower()
        
        score = 0.0
        
        # High value keywords
        for keyword in self.specificity_keywords.get("high", []):
            if keyword.lower() in text_lower:
                score += 0.4
        
        # Medium value keywords
        for keyword in self.specificity_keywords.get("medium", []):
            if keyword.lower() in text_lower:
                score += 0.2
        
        # Penalty for low-value keywords
        for keyword in self.specificity_keywords.get("low", []):
            if keyword.lower() in text_lower:
                score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _score_type(self, content_type: Optional[str], url: str) -> float:
        """Score based on content type preference."""
        # Infer from content-type header or URL extension
        type_str = ""
        
        if content_type:
            type_str = content_type.lower()
        else:
            url_lower = url.lower()
            if url_lower.endswith('.pdf'):
                type_str = 'pdf'
            elif url_lower.endswith('.zip'):
                type_str = 'zip'
            else:
                type_str = 'html'
        
        # Apply boost
        if 'pdf' in type_str:
            return self.type_preferences.get("pdf", 1.5)
        elif 'zip' in type_str:
            return self.type_preferences.get("zip", 1.3)
        else:
            return self.type_preferences.get("html", 1.0)
    
    def _score_anchorability(self, snippet: Optional[str]) -> float:
        """Score based on presence of structural markers."""
        if not snippet:
            return 0.0
        
        count = 0
        for marker in self.anchor_markers:
            if marker in snippet:
                count += 1
        
        # Max 0.2 boost
        return min(0.2, count * 0.05)


```

## [30] common/__init__.py

```python
# FILE: common/__init__.py
# FULL: C:\Projetos\agentic-reg-ingest\common\__init__.py
# NOTE: Concatenated snapshot for review
"""Common utilities and settings."""


```

## [31] common/env_readers.py

```python
# FILE: common/env_readers.py
# FULL: C:\Projetos\agentic-reg-ingest\common\env_readers.py
# NOTE: Concatenated snapshot for review
"""Utilities for reading YAML configs with ${VAR} placeholder resolution."""

import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml


def _smart_cast(value: str) -> Any:
    """
    Smart cast string to appropriate type (int, float, bool, or str).
    
    Args:
        value: String value to cast
        
    Returns:
        Value cast to appropriate type
    """
    # Try int
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Try bool (case insensitive)
    lower_val = value.lower()
    if lower_val in ('true', 'yes', '1'):
        return True
    elif lower_val in ('false', 'no', '0'):
        return False
    
    # Return as string
    return value


def resolve_env_vars(value: Any) -> Any:
    """
    Recursively resolve ${VAR} placeholders in strings using environment variables.
    
    Environment variables are automatically cast to appropriate types:
    - "30" → 30 (int)
    - "3.14" → 3.14 (float)
    - "true" → True (bool)
    - Other → str
    
    Args:
        value: Value to resolve (can be str, dict, list, etc.)
        
    Returns:
        Resolved value with environment variables substituted
    """
    if isinstance(value, str):
        # Check if entire value is a single ${VAR} placeholder
        pattern = r'^\$\{([^}]+)\}$'
        match = re.match(pattern, value)
        
        if match:
            # Full replacement - return with type casting
            var_name = match.group(1)
            env_value = os.getenv(var_name, '')
            if env_value:
                return _smart_cast(env_value)
            else:
                # Variable not set, return placeholder as-is
                return value
        
        # Partial replacement - find all ${VAR} patterns (keep as string)
        pattern = r'\$\{([^}]+)\}'
        
        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        return re.sub(pattern, replacer, value)
    
    elif isinstance(value, dict):
        return {k: resolve_env_vars(v) for k, v in value.items()}
    
    elif isinstance(value, list):
        return [resolve_env_vars(item) for item in value]
    
    else:
        return value


def load_yaml_with_env(yaml_path: Path | str) -> Dict[str, Any]:
    """
    Load a YAML file and resolve ${VAR} placeholders with environment variables.
    
    Args:
        yaml_path: Path to YAML file
        
    Returns:
        Dictionary with resolved configuration
        
    Raises:
        FileNotFoundError: If YAML file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    yaml_path = Path(yaml_path)
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        raw_config = yaml.safe_load(f)
    
    return resolve_env_vars(raw_config)


```

## [32] common/settings.py

```python
# FILE: common/settings.py
# FULL: C:\Projetos\agentic-reg-ingest\common\settings.py
# NOTE: Concatenated snapshot for review
"""Application settings loaded from .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Google CSE
    google_api_key: str
    google_cx: str

    # OpenAI
    openai_api_key: str

    # MySQL
    mysql_host: str
    mysql_port: int = 3306
    mysql_db: str
    mysql_user: str
    mysql_password: str
    mysql_ssl_ca: str = ""

    # Application
    log_level: str = "INFO"
    request_timeout_seconds: int = 30
    ttl_days: int = 7

    # Qdrant (optional)
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "kb_regulatory"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()


```

## [33] docker-compose.yml

```yaml
# FILE: docker-compose.yml
# FULL: C:\Projetos\agentic-reg-ingest\docker-compose.yml
# NOTE: Concatenated snapshot for review
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: agentic-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_PASSWORD:-rootpassword}
      MYSQL_DB: ${MYSQL_DB:-reg_cache}
      MYSQL_USER: ${MYSQL_USER:-reguser}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-regpassword}
    ports:
      - "${MYSQL_PORT:-3306}:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./db/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: [ "CMD", "mysqladmin", "ping", "-h", "localhost" ]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    container_name: agentic-api
    env_file:
      - .env
    environment:
      MYSQL_HOST: mysql
      MYSQL_PORT: 3306
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./configs:/app/configs
    depends_on:
      mysql:
        condition: service_healthy
    command: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

  qdrant:
    image: qdrant/qdrant:latest
    container_name: agentic-qdrant
    ports:
      - "${QDRANT_PORT:-6333}:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__HTTP_PORT: 6333

volumes:
  mysql_data:
  qdrant_data:



```

## [34] ingestion/__init__.py

```python
# FILE: ingestion/__init__.py
# FULL: C:\Projetos\agentic-reg-ingest\ingestion\__init__.py
# NOTE: Concatenated snapshot for review
"""Ingestion utilities for chunking, anchoring, and emitting."""


```

## [35] ingestion/anchors.py

```python
# FILE: ingestion/anchors.py
# FULL: C:\Projetos\agentic-reg-ingest\ingestion\anchors.py
# NOTE: Concatenated snapshot for review
"""Anchor detection and extraction from documents."""

import re
from typing import Any, Dict, List, Optional


class AnchorDetector:
    """Detect structural anchors in document text."""
    
    def __init__(self, markers: List[Dict[str, Any]]):
        """
        Initialize anchor detector with markers.
        
        Args:
            markers: List of marker dicts with 'type', 'pattern', 'confidence'
        """
        self.markers = markers
        self.compiled_patterns = [
            {
                "type": m["type"],
                "pattern": re.compile(m["pattern"], re.IGNORECASE | re.MULTILINE),
                "confidence": m.get("confidence", 0.5),
            }
            for m in markers
        ]
    
    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect anchors in text.
        
        Args:
            text: Document text
            
        Returns:
            List of detected anchors with position, type, and matched text
        """
        anchors = []
        
        for marker in self.compiled_patterns:
            for match in marker["pattern"].finditer(text):
                anchors.append({
                    "type": marker["type"],
                    "matched_text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": marker["confidence"],
                })
        
        # Sort by position
        anchors.sort(key=lambda a: a["start"])
        
        return anchors
    
    def segment_by_anchors(
        self,
        text: str,
        min_segment_length: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Segment text by detected anchors.
        
        Args:
            text: Document text
            min_segment_length: Minimum segment length in characters
            
        Returns:
            List of segments with anchor metadata
        """
        anchors = self.detect(text)
        
        if not anchors:
            # No anchors, return whole text as one segment
            return [{
                "text": text,
                "anchor": None,
                "start": 0,
                "end": len(text),
            }]
        
        segments = []
        
        for i, anchor in enumerate(anchors):
            # Segment starts at current anchor
            start = anchor["start"]
            
            # Segment ends at next anchor or end of text
            if i + 1 < len(anchors):
                end = anchors[i + 1]["start"]
            else:
                end = len(text)
            
            segment_text = text[start:end]
            
            # Skip very short segments
            if len(segment_text.strip()) < min_segment_length:
                continue
            
            segments.append({
                "text": segment_text,
                "anchor": anchor,
                "start": start,
                "end": end,
            })
        
        return segments


```

## [36] ingestion/chunkers.py

```python
# FILE: ingestion/chunkers.py
# FULL: C:\Projetos\agentic-reg-ingest\ingestion\chunkers.py
# NOTE: Concatenated snapshot for review
"""Text chunking utilities with token-aware splitting."""

import structlog
import tiktoken
from typing import Any, Dict, List, Optional

logger = structlog.get_logger()


class TokenAwareChunker:
    """Chunk text based on token counts with overlap."""
    
    def __init__(
        self,
        min_tokens: int = 100,
        max_tokens: int = 512,
        overlap_tokens: int = 50,
        encoding: str = "cl100k_base",
    ):
        """
        Initialize chunker.
        
        Args:
            min_tokens: Minimum chunk size in tokens
            max_tokens: Maximum chunk size in tokens
            overlap_tokens: Overlap between chunks in tokens
            encoding: Tiktoken encoding name
        """
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoder = tiktoken.get_encoding(encoding)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
    
    def chunk(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        anchors: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Chunk text into token-sized pieces with optional anchor-aware splitting.
        
        Args:
            text: Input text
            metadata: Optional metadata to attach to each chunk
            anchors: Optional list of anchor dicts with 'type' and 'value' keys
            
        Returns:
            List of chunks with text and metadata
        """
        # Validate input
        if not text or not text.strip():
            logger.warning("chunker_empty_text")
            raise ValueError("Cannot chunk empty text")
        
        try:
            # Encode to tokens
            tokens = self.encoder.encode(text)
        except Exception as e:
            logger.error(
                "chunker_encode_failed",
                error_type=type(e).__name__,
                error_message=str(e),
                text_preview=text[:200] if text else "",
            )
            raise ValueError(f"Failed to encode text: {e}")
        
        if len(tokens) == 0:
            logger.warning("chunker_no_tokens")
            raise ValueError("Text encoded to zero tokens")
        
        if len(tokens) <= self.max_tokens:
            # Text fits in one chunk
            return [{
                "text": text,
                "tokens": len(tokens),
                "chunk_index": 0,
                "total_chunks": 1,
                **(metadata or {}),
            }]
        
        # If anchors provided, try anchor-aware splitting
        if anchors:
            return self._chunk_with_anchors_aware(text, tokens, anchors, metadata)
        
        # Otherwise, standard token window chunking
        return self._chunk_standard(text, tokens, metadata)
    
    def _chunk_standard(
        self,
        text: str,
        tokens: List[int],
        metadata: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Standard token window chunking without anchors."""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(tokens):
            # Get chunk tokens
            end = min(start + self.max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            try:
                chunk_text = self.encoder.decode(chunk_tokens)
            except Exception as e:
                logger.error(
                    "chunker_decode_failed",
                    chunk_index=chunk_index,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise ValueError(f"Failed to decode chunk {chunk_index}: {e}")
            
            chunks.append({
                "text": chunk_text,
                "tokens": len(chunk_tokens),
                "chunk_index": chunk_index,
                "start_token": start,
                "end_token": end,
                **(metadata or {}),
            })
            
            # Move to next chunk with overlap
            start += self.max_tokens - self.overlap_tokens
            chunk_index += 1
        
        # Update total_chunks
        for chunk in chunks:
            chunk["total_chunks"] = len(chunks)
        
        return chunks
    
    def _chunk_with_anchors_aware(
        self,
        text: str,
        tokens: List[int],
        anchors: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Anchor-aware chunking: try to start new chunks near headings/tables.
        
        Strategy:
        1. Find approximate character positions of anchor texts in document
        2. Convert char positions to token positions
        3. Try to start chunks near anchor boundaries
        4. Still respect min/max token limits
        """
        # Find anchor positions in text
        anchor_positions = []
        for anchor in anchors:
            anchor_text = anchor.get("value", "")
            if not anchor_text:
                continue
            
            # Find this anchor in the text
            pos = text.find(anchor_text)
            if pos >= 0:
                anchor_positions.append({
                    "char_pos": pos,
                    "anchor": anchor,
                })
        
        # Sort by position
        anchor_positions.sort(key=lambda x: x["char_pos"])
        
        if not anchor_positions:
            # No anchors found in text, fallback to standard
            logger.debug("no_anchors_found_in_text", anchors_count=len(anchors))
            return self._chunk_standard(text, tokens, metadata)
        
        # Convert character positions to approximate token positions
        # This is approximate since tokenization doesn't map 1:1 to characters
        text_len = len(text)
        token_positions = []
        for ap in anchor_positions:
            # Approximate token position based on character ratio
            approx_token_pos = int((ap["char_pos"] / text_len) * len(tokens))
            token_positions.append({
                "token_pos": approx_token_pos,
                "anchor": ap["anchor"],
            })
        
        # Create chunks respecting anchor boundaries
        chunks = []
        start = 0
        chunk_index = 0
        next_anchor_idx = 0
        
        while start < len(tokens):
            # Look for next anchor within reasonable range
            preferred_end = start + self.max_tokens
            
            # Check if there's an anchor between start and preferred_end
            split_at = None
            while next_anchor_idx < len(token_positions):
                anchor_pos = token_positions[next_anchor_idx]["token_pos"]
                
                if anchor_pos <= start:
                    # Already passed this anchor
                    next_anchor_idx += 1
                    continue
                
                if start + self.min_tokens <= anchor_pos <= preferred_end:
                    # Good split point: anchor within valid range
                    split_at = anchor_pos
                    next_anchor_idx += 1
                    break
                
                if anchor_pos > preferred_end:
                    # Anchor too far, use max_tokens
                    break
                
                next_anchor_idx += 1
            
            if split_at:
                end = split_at
            else:
                end = min(preferred_end, len(tokens))
            
            chunk_tokens = tokens[start:end]
            
            try:
                chunk_text = self.encoder.decode(chunk_tokens)
            except Exception as e:
                logger.error(
                    "chunker_decode_failed",
                    chunk_index=chunk_index,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise ValueError(f"Failed to decode chunk {chunk_index}: {e}")
            
            chunks.append({
                "text": chunk_text,
                "tokens": len(chunk_tokens),
                "chunk_index": chunk_index,
                "start_token": start,
                "end_token": end,
                **(metadata or {}),
            })
            
            # Move to next chunk with overlap
            start += len(chunk_tokens) - self.overlap_tokens
            chunk_index += 1
        
        # Update total_chunks
        for chunk in chunks:
            chunk["total_chunks"] = len(chunks)
        
        logger.debug(
            "anchor_aware_chunking_done",
            chunks_count=len(chunks),
            anchors_used=len(anchor_positions),
        )
        
        return chunks
    
    def chunk_with_anchors(
        self,
        segments: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Chunk text segments that were split by anchors.
        
        Args:
            segments: List of segments from AnchorDetector
            
        Returns:
            List of chunks with anchor metadata
        """
        all_chunks = []
        
        for seg_idx, segment in enumerate(segments):
            text = segment["text"]
            anchor = segment.get("anchor")
            
            # Create metadata
            metadata = {
                "segment_index": seg_idx,
                "anchor_type": anchor["type"] if anchor else None,
                "anchor_text": anchor["matched_text"] if anchor else None,
            }
            
            # Chunk this segment
            chunks = self.chunk(text, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks


```

## [37] ingestion/emitters.py

```python
# FILE: ingestion/emitters.py
# FULL: C:\Projetos\agentic-reg-ingest\ingestion\emitters.py
# NOTE: Concatenated snapshot for review
"""Output emitters for knowledge base data."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class JSONLEmitter:
    """Emit chunks as JSONL (one JSON object per line)."""
    
    def __init__(self, output_path: str | Path):
        """
        Initialize emitter.
        
        Args:
            output_path: Path to output JSONL file
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def emit_chunk(
        self,
        chunk: Dict[str, Any],
        source_url: str,
        source_file: str,
        append: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit a single chunk to JSONL.
        
        Args:
            chunk: Chunk dictionary
            source_url: Source document URL
            source_file: Local file path (if downloaded)
            append: Append to file (True) or overwrite (False)
            metadata: Additional metadata (content_type, extracted_by, etc.)
        """
        record = {
            "text": chunk["text"],
            "tokens": chunk["tokens"],
            "chunk_index": chunk["chunk_index"],
            "total_chunks": chunk.get("total_chunks", 1),
            "source_url": source_url,
            "source_file": source_file,
            "segment_index": chunk.get("segment_index"),
            "anchor_type": chunk.get("anchor_type"),
            "anchor_text": chunk.get("anchor_text"),
        }
        
        # Add metadata if provided
        if metadata:
            record["metadata"] = metadata
        
        mode = 'a' if append else 'w'
        
        with open(self.output_path, mode, encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def emit_chunks(
        self,
        chunks: List[Dict[str, Any]],
        source_url: str,
        source_file: str,
        append: bool = True,
        anchors: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit multiple chunks to JSONL.
        
        Args:
            chunks: List of chunk dictionaries
            source_url: Source document URL
            source_file: Local file path
            append: Append to file
            anchors: Optional list of anchors detected in document
            metadata: Optional metadata (content_type, extracted_by, etc.)
        """
        # Add anchors info to metadata if provided
        if metadata is None:
            metadata = {}
        
        if anchors:
            metadata["anchors_count"] = len(anchors)
            metadata["anchors"] = anchors
        
        for chunk in chunks:
            self.emit_chunk(chunk, source_url, source_file, append=append, metadata=metadata)
            # After first chunk, always append
            append = True
    
    def clear(self) -> None:
        """Clear output file."""
        if self.output_path.exists():
            self.output_path.unlink()


```

## [38] pipelines/__init__.py

```python
# FILE: pipelines/__init__.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\__init__.py
# NOTE: Concatenated snapshot for review
"""Pipeline modules for search and ingestion."""


```

## [39] pipelines/agentic_controller.py

```python
# FILE: pipelines/agentic_controller.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\agentic_controller.py
# NOTE: Concatenated snapshot for review
"""Agentic Search Controller: Plan→Act→Observe→Judge→Re-plan loop."""

import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, List

import structlog
import requests
from sqlalchemy.orm import Session

from agentic.cse_client import CSEClient
from agentic.detect import detect_type, _url_ext
from agentic.llm import LLMClient
from agentic.normalize import extract_domain, normalize_url
from agentic.quality import apply_quality_gates, count_anchor_signals
from agentic.schemas import (
    AgenticResult,
    CandidateSummary,
    Plan,
    RejectedSummary,
)
from agentic.scoring import ResultScorer
from db.dao import AgenticIterDAO, AgenticPlanDAO, DocumentCatalogDAO, SearchQueryDAO, SearchResultDAO

logger = structlog.get_logger()


class AgenticSearchController:
    """Controller for agentic search with Plan→Act→Observe→Judge→Re-plan loop."""
    
    def __init__(
        self,
        cse_client: CSEClient,
        llm_client: LLMClient,
        scorer: ResultScorer,
        timeout: int = 20,
    ):
        """
        Initialize agentic controller.
        
        Args:
            cse_client: Google CSE client
            llm_client: LLM client for planning and judging
            scorer: Result scorer
            timeout: HTTP timeout for metadata fetching
        """
        self.cse = cse_client
        self.llm = llm_client
        self.scorer = scorer
        self.timeout = timeout
    
    def run_agentic_search(
        self,
        plan: Plan,
        session: Session,
    ) -> AgenticResult:
        """
        Execute agentic search loop.
        
        Steps per iteration:
        1. Select queries (up to max_queries_per_iter)
        2. ACT: Execute CSE searches
        3. OBSERVE: Fetch metadata, detect types, score candidates
        4. JUDGE: Apply quality gates + LLM judgment
        5. PERSIST: Save iteration results
        6. CHECK STOP CONDITIONS
        7. RE-PLAN: Merge new queries
        
        Args:
            plan: Search plan
            session: Database session
            
        Returns:
            AgenticResult with stats and promoted URLs
        """
        plan_id = str(uuid.uuid4())
        
        logger.info(
            "agentic_search_start",
            plan_id=plan_id,
            goal=plan.goal,
            queries_count=len(plan.queries),
        )
        
        # Save plan to DB
        AgenticPlanDAO.save_plan(
            session,
            plan_id=plan_id,
            goal=plan.goal,
            plan_json=plan.dict(),
        )
        session.commit()
        
        # Initialize tracking
        all_approved_urls = set()
        all_approved_candidates = []
        executed_queries_total = set()
        pending_queries = [q.q for q in plan.queries]
        cse_calls_count = 0
        
        # Main agentic loop
        for iteration in range(1, plan.stop.max_iterations + 1):
            logger.info("agentic_iteration_start", iteration=iteration, plan_id=plan_id)
            
            # STEP 1: Select queries for this iteration
            queries_this_iter = pending_queries[:plan.stop.max_queries_per_iter]
            
            if not queries_this_iter:
                logger.info("agentic_no_queries", iteration=iteration)
                result = AgenticResult(
                    plan_id=plan_id,
                    iterations=iteration - 1,
                    approved_total=len(all_approved_urls),
                    stopped_by="no_queries",
                    promoted_urls=list(all_approved_urls),
                )
                return result
            
            # STEP 2: ACT - Execute CSE searches
            all_candidates = []
            
            for query in queries_this_iter:
                # Check budget
                if cse_calls_count >= plan.budget.max_cse_calls:
                    logger.warning("agentic_budget_exceeded", calls=cse_calls_count)
                    break
                
                logger.info("agentic_cse_query", query=query)
                
                try:
                    # Get k results for this query
                    query_spec = next((q for q in plan.queries if q.q == query), None)
                    k = query_spec.k if query_spec else 10
                    
                    items = self.cse.search_all(
                        query=query,
                        max_results=k,
                        results_per_page=10,
                    )
                    
                    cse_calls_count += 1
                    
                    logger.info("agentic_cse_results", query=query, count=len(items))
                    
                    # STEP 3: OBSERVE - Process each hit
                    for item in items:
                        url = normalize_url(item.get("link", ""))
                        
                        # Skip if already approved
                        if url in all_approved_urls:
                            continue
                        
                        # Check deny patterns
                        if self._matches_deny_pattern(url, plan.deny_patterns):
                            logger.debug("agentic_denied_pattern", url=url)
                            continue
                        
                        # Check allow domains
                        if plan.allow_domains and not self._matches_allow_domains(url, plan.allow_domains):
                            logger.debug("agentic_not_in_allowlist", url=url)
                            continue
                        
                        # Fetch metadata
                        candidate = self._build_candidate(url, item, plan)
                        
                        if candidate:
                            all_candidates.append(candidate)
                
                except Exception as e:
                    logger.error("agentic_cse_error", query=query, error=str(e))
                    continue
            
            executed_queries_total.update(queries_this_iter)
            
            logger.info(
                "agentic_observe_done",
                iteration=iteration,
                candidates_count=len(all_candidates),
            )
            
            # STEP 4: JUDGE - Apply quality gates + LLM
            approved_this_iter = []
            rejected_this_iter = []
            
            # 4a. Hard quality gates (code-level)
            filtered_candidates = []
            for candidate in all_candidates:
                passed, violations = apply_quality_gates(plan.quality_gates, candidate)
                
                if passed:
                    filtered_candidates.append(candidate)
                else:
                    rejected_this_iter.append(RejectedSummary(
                        url=candidate.url,
                        reason="Quality gates failed",
                        violations=violations,
                    ))
            
            logger.info(
                "agentic_quality_gates_applied",
                iteration=iteration,
                passed=len(filtered_candidates),
                rejected=len(rejected_this_iter),
            )
            
            # 4b. LLM judge (semantic)
            if filtered_candidates:
                judge_response = self.llm.judge_candidates(plan, filtered_candidates)
                
                # Collect approved
                for url in judge_response.approved_urls:
                    # Find candidate
                    cand = next((c for c in filtered_candidates if c.url == url), None)
                    if cand and url not in all_approved_urls:
                        approved_this_iter.append(cand)
                        all_approved_urls.add(url)
                        all_approved_candidates.append(cand)
                
                # Collect LLM rejections
                rejected_this_iter.extend(judge_response.rejected)
                
                new_queries = judge_response.new_queries[:3]  # Cap at 3
            else:
                new_queries = []
            
            logger.info(
                "agentic_judge_done",
                iteration=iteration,
                approved=len(approved_this_iter),
                rejected=len(rejected_this_iter),
                new_queries=len(new_queries),
            )
            
            # STEP 5: PERSIST - Save iteration
            AgenticIterDAO.save_iter(
                session,
                plan_id=plan_id,
                iter_num=iteration,
                executed_queries=queries_this_iter,
                approved_urls=[c.url for c in approved_this_iter],
                rejected_json=[r.dict() for r in rejected_this_iter],
                new_queries=new_queries,
                summary=f"Iter {iteration}: {len(approved_this_iter)} approved, {len(rejected_this_iter)} rejected",
            )
            
            # Persist approved to search_result
            self._persist_approved(session, plan, approved_this_iter)
            
            session.commit()
            
            logger.info(
                "agentic_iteration_complete",
                iteration=iteration,
                total_approved=len(all_approved_urls),
            )
            
            # STEP 6: CHECK STOP CONDITIONS
            
            # 6a. Minimum approved reached
            if len(all_approved_urls) >= plan.stop.min_approved:
                logger.info(
                    "agentic_stop_min_approved",
                    approved=len(all_approved_urls),
                    target=plan.stop.min_approved,
                )
                return AgenticResult(
                    plan_id=plan_id,
                    iterations=iteration,
                    approved_total=len(all_approved_urls),
                    stopped_by="min_approved",
                    promoted_urls=list(all_approved_urls),
                )
            
            # 6b. Budget exceeded
            if cse_calls_count >= plan.budget.max_cse_calls:
                logger.info("agentic_stop_budget", calls=cse_calls_count)
                return AgenticResult(
                    plan_id=plan_id,
                    iterations=iteration,
                    approved_total=len(all_approved_urls),
                    stopped_by="budget",
                    promoted_urls=list(all_approved_urls),
                )
            
            # 6c. No progress (no approvals and no new queries)
            if not approved_this_iter and not new_queries:
                logger.info("agentic_stop_no_progress", iteration=iteration)
                return AgenticResult(
                    plan_id=plan_id,
                    iterations=iteration,
                    approved_total=len(all_approved_urls),
                    stopped_by="no_progress",
                    promoted_urls=list(all_approved_urls),
                )
            
            # STEP 7: RE-PLAN - Merge new queries
            pending_queries = [q for q in pending_queries if q not in queries_this_iter]
            pending_queries.extend(new_queries)
            
            # Dedup while preserving order
            seen = set()
            deduped = []
            for q in pending_queries:
                if q not in seen:
                    seen.add(q)
                    deduped.append(q)
            pending_queries = deduped
            
            logger.info(
                "agentic_replan",
                iteration=iteration,
                pending_queries=len(pending_queries),
                new_queries_added=len(new_queries),
            )
        
        # Reached max iterations
        logger.info("agentic_stop_max_iterations", iterations=plan.stop.max_iterations)
        return AgenticResult(
            plan_id=plan_id,
            iterations=plan.stop.max_iterations,
            approved_total=len(all_approved_urls),
            stopped_by="max_iterations",
            promoted_urls=list(all_approved_urls),
        )
    
    def _build_candidate(
        self,
        url: str,
        cse_item: Dict[str, Any],
        plan: Plan,
    ) -> CandidateSummary | None:
        """
        Build candidate summary from CSE item with metadata.
        
        Args:
            url: Normalized URL
            cse_item: CSE search result item
            plan: Search plan
            
        Returns:
            CandidateSummary or None if failed
        """
        try:
            title = cse_item.get("title", "")
            snippet = cse_item.get("snippet", "")
            
            # Fetch metadata via HEAD
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                headers = dict(response.headers)
            except Exception as e:
                logger.debug("agentic_head_failed", url=url, error=str(e))
                headers = {}
            
            # Detect document type
            typing_info = detect_type(url, headers, sniff_magic=False)
            
            # Score
            content_type = headers.get("Content-Type")
            last_modified_str = headers.get("Last-Modified")
            last_modified = None
            if last_modified_str:
                try:
                    last_modified = datetime.strptime(
                        last_modified_str,
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )
                except Exception:
                    pass
            
            score = self.scorer.score(
                url=url,
                title=title,
                snippet=snippet,
                content_type=content_type,
                last_modified=last_modified,
            )
            
            # Count anchor signals
            combined_text = f"{title} {snippet}"
            anchor_signals = count_anchor_signals(combined_text)
            
            candidate = CandidateSummary(
                url=url,
                title=title,
                snippet=snippet,
                headers=headers,
                score=score,
                final_type=typing_info.get("final_type", "unknown"),
                anchor_signals=anchor_signals,
            )
            
            logger.debug(
                "agentic_candidate_built",
                url=url,
                score=score,
                final_type=candidate.final_type,
                anchor_signals=anchor_signals,
            )
            
            return candidate
        
        except Exception as e:
            logger.error("agentic_candidate_error", url=url, error=str(e))
            return None
    
    def _matches_deny_pattern(self, url: str, patterns: List[str]) -> bool:
        """Check if URL matches any deny pattern."""
        import re
        
        for pattern in patterns:
            try:
                if re.search(pattern, url, re.IGNORECASE):
                    return True
            except Exception:
                continue
        return False
    
    def _matches_allow_domains(self, url: str, domains: List[str]) -> bool:
        """
        Check if URL belongs to allowed domains/paths.
        
        Supports both domain matching and path prefix matching:
        - "www.gov.br" matches any URL from www.gov.br
        - "www.gov.br/ans" matches URLs starting with www.gov.br/ans
        """
        domain = extract_domain(url)
        
        for allowed in domains:
            # Check if it's a domain-only match (no path)
            if '/' not in allowed:
                # Pure domain match
                if allowed in domain or domain.endswith(f".{allowed}"):
                    return True
            else:
                # Domain + path prefix match
                # Example: "www.gov.br/ans" should match "https://www.gov.br/ans/pt-br/..."
                if allowed in url:
                    return True
                # Also check without protocol
                url_without_protocol = url.replace("https://", "").replace("http://", "")
                if url_without_protocol.startswith(allowed):
                    return True
        
        return False
    
    def _persist_approved(
        self,
        session: Session,
        plan: Plan,
        approved: List[CandidateSummary],
    ) -> None:
        """
        Persist approved candidates to search_result and document_catalog.
        
        Args:
            session: DB session
            plan: Search plan
            approved: Approved candidates
        """
        if not approved:
            return
        
        # Create a search_query record for this plan iteration
        cache_key = hashlib.sha256(plan.goal.encode()).hexdigest()
        
        try:
            query_record = SearchQueryDAO.create(
                session,
                cache_key=cache_key,
                cx="agentic",  # Special marker
                query_text=plan.goal,
                allow_domains="|".join(plan.allow_domains) if plan.allow_domains else None,
                top_n=len(approved),
                ttl_days=plan.budget.ttl_days,
            )
        except Exception:
            # Query might already exist, find it
            query_record = SearchQueryDAO.find_by_cache_key(session, cache_key)
            if not query_record:
                logger.error("agentic_query_record_failed")
                return
        
        # Create search_result records
        for idx, candidate in enumerate(approved):
            # Parse last_modified
            last_modified = None
            last_modified_str = candidate.headers.get("Last-Modified")
            if last_modified_str:
                try:
                    last_modified = datetime.strptime(
                        last_modified_str,
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )
                except Exception:
                    pass
            
            try:
                SearchResultDAO.create(
                    session,
                    query_id=query_record.id,
                    url=candidate.url,
                    title=candidate.title,
                    snippet=candidate.snippet,
                    rank_position=idx + 1,
                    score=candidate.score,
                    content_type=candidate.headers.get("Content-Type"),
                    last_modified=last_modified,
                    approved=True,
                    # Typing fields
                    http_content_type=candidate.headers.get("Content-Type"),
                    http_content_disposition=candidate.headers.get("Content-Disposition"),
                    url_ext=_url_ext(candidate.url),
                    detected_mime=None,  # Could enhance with detect_type full result
                    detected_ext=None,
                    final_type=candidate.final_type,
                    fetch_status="ok",
                )
            except Exception as e:
                logger.warning("agentic_persist_result_failed", url=candidate.url, error=str(e))
            
            # Upsert document_catalog
            domain = extract_domain(candidate.url)
            
            try:
                DocumentCatalogDAO.upsert(
                    session,
                    canonical_url=candidate.url,
                    content_type=candidate.headers.get("Content-Type"),
                    last_modified=last_modified,
                    title=candidate.title,
                    domain=domain,
                    final_type=candidate.final_type,
                )
            except Exception as e:
                logger.warning("agentic_persist_catalog_failed", url=candidate.url, error=str(e))
        
        session.flush()


def run_agentic_search(
    plan: Plan,
    session: Session,
    cse_client: CSEClient,
    llm_client: LLMClient,
    scorer: ResultScorer,
    timeout: int = 20,
) -> AgenticResult:
    """
    Convenience function to run agentic search.
    
    Args:
        plan: Search plan
        session: Database session
        cse_client: Google CSE client
        llm_client: LLM client
        scorer: Result scorer
        timeout: HTTP timeout
        
    Returns:
        AgenticResult
    """
    controller = AgenticSearchController(cse_client, llm_client, scorer, timeout)
    return controller.run_agentic_search(plan, session)


```

## [40] pipelines/executors/__init__.py

```python
# FILE: pipelines/executors/__init__.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\executors\__init__.py
# NOTE: Concatenated snapshot for review
"""Document type-specific ingestors."""


```

## [41] pipelines/executors/html_ingestor.py

```python
# FILE: pipelines/executors/html_ingestor.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\executors\html_ingestor.py
# NOTE: Concatenated snapshot for review
"""HTML document ingestor with LLM structure extraction and PDF wrapper detection."""

import structlog
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic.html_extract import clean_html_to_excerpt, is_probably_pdf_wrapper
from agentic.llm import LLMClient
from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter

logger = structlog.get_logger()


class HTMLIngestor:
    """Ingest HTML documents with LLM-guided structure extraction."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        chunker: TokenAwareChunker,
        emitter: JSONLEmitter,
        llm_client: Optional[LLMClient] = None,
    ):
        """
        Initialize HTML ingestor.
        
        Args:
            config: Ingest configuration
            chunker: Token-aware chunker
            emitter: Output emitter
            llm_client: Optional LLM client for structure extraction
        """
        self.config = config
        self.chunker = chunker
        self.emitter = emitter
        self.llm = llm_client
        
        # Download settings
        self.timeout = config["download"]["timeout"]
        self.user_agent = config["download"]["user_agent"]
        self.min_content_length = config["html"]["min_content_length"]
        
        # LLM extractor settings
        self.llm_extractor_cfg = config.get("llm_html_extractor", {})
        self.llm_enabled = self.llm_extractor_cfg.get("enabled", False)
        self.max_chars = self.llm_extractor_cfg.get("max_chars", 120000)
        self.max_chars_llm = self.llm_extractor_cfg.get("max_chars_llm", 80000)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def download(self, url: str) -> tuple[str, Dict[str, str]]:
        """
        Download HTML content and headers.
        
        Returns:
            Tuple of (html_content, headers_dict)
        """
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text, dict(response.headers)
    
    def ingest(
        self,
        url: str,
        title: Optional[str],
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        expected_type: str = "html",
    ) -> Dict[str, Any]:
        """
        Ingest HTML document with LLM structure extraction.
        
        Returns:
            Dictionary with:
            - ok: bool
            - next_type: 'pdf' | 'html' | 'none'
            - next_url: str | None (PDF URL if wrapper detected)
        """
        # Validate expected type
        if expected_type and expected_type != "html":
            logger.error(
                "html_type_mismatch",
                url=url,
                expected=expected_type,
                executor="html",
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        try:
            # Step 1: Download HTML
            logger.info("html_download_start", url=url)
            html, response_headers = self.download(url)
            logger.info("html_downloaded", url=url, size=len(html))
            
            # Step 2: Check Content-Type
            content_type = response_headers.get("Content-Type", "").lower()
            if content_type and not any(ct in content_type for ct in ["html", "text/"]):
                logger.warning("html_wrong_content_type", url=url, content_type=content_type)
                return {"ok": False, "next_type": "none", "next_url": None}
            
            # Step 3: LLM extractor path (if enabled)
            if self.llm_enabled and self.llm:
                return self._ingest_with_llm(url, title, html, response_headers)
            else:
                # Fallback: readability-only
                return self._ingest_fallback(url, title, html)
        
        except requests.exceptions.RequestException as e:
            logger.error(
                "html_download_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        except Exception as e:
            logger.error(
                "html_ingest_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return {"ok": False, "next_type": "none", "next_url": None}
    
    def _ingest_with_llm(
        self,
        url: str,
        title: Optional[str],
        html: str,
        headers: Dict[str, str],
    ) -> Dict[str, Any]:
        """LLM-powered HTML ingestion with structure extraction."""
        
        # Check if PDF wrapper
        logger.info("html_pdf_wrapper_check", url=url)
        pdf_link = is_probably_pdf_wrapper(html, url)
        if pdf_link:
            logger.info("html_pdf_wrapper_detected", url=url, pdf_link=pdf_link)
            return {"ok": False, "next_type": "pdf", "next_url": pdf_link}
        
        # Extract clean excerpt with anchors
        logger.info("html_extract_start", url=url)
        bundle = clean_html_to_excerpt(html, url, self.max_chars)
        excerpt = bundle["excerpt"]
        pdf_links = bundle["pdf_links"]
        anchors_struct = bundle["anchors_struct"]
        
        logger.info(
            "html_extracted",
            url=url,
            excerpt_len=len(excerpt),
            pdf_links_count=len(pdf_links),
            anchors_count=len(anchors_struct),
        )
        
        # If strong PDF signal (many PDF links), consider routing to PDF
        if len(pdf_links) >= 3:
            logger.info("html_many_pdf_links", url=url, count=len(pdf_links))
            # Return first PDF link for routing
            return {"ok": False, "next_type": "pdf", "next_url": pdf_links[0]}
        
        # Check minimum content length
        if len(excerpt) < self.min_content_length:
            logger.warning(
                "html_content_too_short",
                url=url,
                length=len(excerpt),
                min_required=self.min_content_length,
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        # Call LLM to extract structure
        logger.info("html_llm_struct_start", url=url)
        doc = self.llm.extract_html_structure(url, excerpt, self.max_chars_llm)
        
        # Build content from sections
        if doc.get("sections"):
            content_parts = []
            for section in doc["sections"]:
                heading = section.get("heading", "")
                text = section.get("text", "")
                if heading:
                    content_parts.append(f"# {heading}")
                if text:
                    content_parts.append(text)
            content = "\n\n".join(content_parts)
        else:
            # Fallback to excerpt if no sections
            content = excerpt
        
        # Get anchors (prefer LLM anchors, fallback to struct anchors)
        anchors = doc.get("anchors") if doc.get("anchors") else anchors_struct
        
        logger.info(
            "html_llm_struct_done",
            url=url,
            sections_count=len(doc.get("sections", [])),
            anchors_count=len(anchors),
        )
        
        # Chunking with anchors
        logger.info("html_chunking_start", url=url)
        chunks = self.chunker.chunk(content, anchors=anchors)
        logger.info("html_chunked", url=url, num_chunks=len(chunks))
        
        # Emit chunks with metadata
        metadata = {
            "content_type": "text/html",
            "extracted_by": "llm+readability",
            "llm_model": self.llm_extractor_cfg.get("model"),
            "language": doc.get("language", "unknown"),
            "sections_count": len(doc.get("sections", [])),
        }
        
        logger.info("html_emit_start", url=url)
        self.emitter.emit_chunks(
            chunks=chunks,
            source_url=url,
            source_file="",
            anchors=anchors,
            metadata=metadata,
        )
        logger.info("html_ingest_complete", url=url)
        
        return {"ok": True, "next_type": "none", "next_url": None}
    
    def _ingest_fallback(
        self,
        url: str,
        title: Optional[str],
        html: str,
    ) -> Dict[str, Any]:
        """Fallback HTML ingestion without LLM (readability only)."""
        
        logger.info("html_extract_start", url=url)
        bundle = clean_html_to_excerpt(html, url, self.max_chars)
        content = bundle["excerpt"]
        anchors = bundle["anchors_struct"]
        
        logger.info("html_extracted", url=url, content_length=len(content))
        
        if len(content) < self.min_content_length:
            logger.warning(
                "html_content_too_short",
                url=url,
                length=len(content),
                min_required=self.min_content_length,
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        # Chunk content
        logger.info("html_chunking_start", url=url)
        chunks = self.chunker.chunk(content, anchors=anchors if anchors else None)
        logger.info("html_chunked", url=url, num_chunks=len(chunks))
        
        # Emit
        metadata = {
            "content_type": "text/html",
            "extracted_by": "readability",
        }
        
        logger.info("html_emit_start", url=url)
        self.emitter.emit_chunks(
            chunks=chunks,
            source_url=url,
            source_file="",
            anchors=anchors if anchors else None,
            metadata=metadata,
        )
        logger.info("html_ingest_complete", url=url)
        
        return {"ok": True, "next_type": "none", "next_url": None}


```

## [42] pipelines/executors/html_ingestor_new.py

```python
# FILE: pipelines/executors/html_ingestor_new.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\executors\html_ingestor_new.py
# NOTE: Concatenated snapshot for review
"""HTML document ingestor with LLM structure extraction and PDF wrapper detection."""

import structlog
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic.html_extract import clean_html_to_excerpt, is_probably_pdf_wrapper
from agentic.llm import LLMClient
from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter

logger = structlog.get_logger()


class HTMLIngestor:
    """Ingest HTML documents with LLM-guided structure extraction."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        chunker: TokenAwareChunker,
        emitter: JSONLEmitter,
        llm_client: Optional[LLMClient] = None,
    ):
        """
        Initialize HTML ingestor.
        
        Args:
            config: Ingest configuration
            chunker: Token-aware chunker
            emitter: Output emitter
            llm_client: Optional LLM client for structure extraction
        """
        self.config = config
        self.chunker = chunker
        self.emitter = emitter
        self.llm = llm_client
        
        # Download settings
        self.timeout = config["download"]["timeout"]
        self.user_agent = config["download"]["user_agent"]
        self.min_content_length = config["html"]["min_content_length"]
        
        # LLM extractor settings
        self.llm_extractor_cfg = config.get("llm_html_extractor", {})
        self.llm_enabled = self.llm_extractor_cfg.get("enabled", False)
        self.max_chars = self.llm_extractor_cfg.get("max_chars", 120000)
        self.max_chars_llm = self.llm_extractor_cfg.get("max_chars_llm", 80000)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def download(self, url: str) -> tuple[str, Dict[str, str]]:
        """
        Download HTML content and headers.
        
        Returns:
            Tuple of (html_content, headers_dict)
        """
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text, dict(response.headers)
    
    def ingest(
        self,
        url: str,
        title: Optional[str],
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        expected_type: str = "html",
    ) -> Dict[str, Any]:
        """
        Ingest HTML document with LLM structure extraction.
        
        Returns:
            Dictionary with:
            - ok: bool
            - next_type: 'pdf' | 'html' | 'none'
            - next_url: str | None (PDF URL if wrapper detected)
        """
        # Validate expected type
        if expected_type and expected_type != "html":
            logger.error(
                "html_type_mismatch",
                url=url,
                expected=expected_type,
                executor="html",
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        try:
            # Step 1: Download HTML
            logger.info("html_download_start", url=url)
            html, response_headers = self.download(url)
            logger.info("html_downloaded", url=url, size=len(html))
            
            # Step 2: Check Content-Type
            content_type = response_headers.get("Content-Type", "").lower()
            if content_type and not any(ct in content_type for ct in ["html", "text/"]):
                logger.warning("html_wrong_content_type", url=url, content_type=content_type)
                return {"ok": False, "next_type": "none", "next_url": None}
            
            # Step 3: LLM extractor path (if enabled)
            if self.llm_enabled and self.llm:
                return self._ingest_with_llm(url, title, html, response_headers)
            else:
                # Fallback: readability-only
                return self._ingest_fallback(url, title, html)
        
        except requests.exceptions.RequestException as e:
            logger.error(
                "html_download_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        except Exception as e:
            logger.error(
                "html_ingest_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return {"ok": False, "next_type": "none", "next_url": None}
    
    def _ingest_with_llm(
        self,
        url: str,
        title: Optional[str],
        html: str,
        headers: Dict[str, str],
    ) -> Dict[str, Any]:
        """LLM-powered HTML ingestion with structure extraction."""
        
        # Check if PDF wrapper
        logger.info("html_pdf_wrapper_check", url=url)
        pdf_link = is_probably_pdf_wrapper(html, url)
        if pdf_link:
            logger.info("html_pdf_wrapper_detected", url=url, pdf_link=pdf_link)
            return {"ok": False, "next_type": "pdf", "next_url": pdf_link}
        
        # Extract clean excerpt with anchors
        logger.info("html_extract_start", url=url)
        bundle = clean_html_to_excerpt(html, url, self.max_chars)
        excerpt = bundle["excerpt"]
        pdf_links = bundle["pdf_links"]
        anchors_struct = bundle["anchors_struct"]
        
        logger.info(
            "html_extracted",
            url=url,
            excerpt_len=len(excerpt),
            pdf_links_count=len(pdf_links),
            anchors_count=len(anchors_struct),
        )
        
        # If strong PDF signal (many PDF links), consider routing to PDF
        if len(pdf_links) >= 3:
            logger.info("html_many_pdf_links", url=url, count=len(pdf_links))
            # Return first PDF link for routing
            return {"ok": False, "next_type": "pdf", "next_url": pdf_links[0]}
        
        # Check minimum content length
        if len(excerpt) < self.min_content_length:
            logger.warning(
                "html_content_too_short",
                url=url,
                length=len(excerpt),
                min_required=self.min_content_length,
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        # Call LLM to extract structure
        logger.info("html_llm_struct_start", url=url)
        doc = self.llm.extract_html_structure(url, excerpt, self.max_chars_llm)
        
        # Build content from sections
        if doc.get("sections"):
            content_parts = []
            for section in doc["sections"]:
                heading = section.get("heading", "")
                text = section.get("text", "")
                if heading:
                    content_parts.append(f"# {heading}")
                if text:
                    content_parts.append(text)
            content = "\n\n".join(content_parts)
        else:
            # Fallback to excerpt if no sections
            content = excerpt
        
        # Get anchors (prefer LLM anchors, fallback to struct anchors)
        anchors = doc.get("anchors") if doc.get("anchors") else anchors_struct
        
        logger.info(
            "html_llm_struct_done",
            url=url,
            sections_count=len(doc.get("sections", [])),
            anchors_count=len(anchors),
        )
        
        # Chunking with anchors
        logger.info("html_chunking_start", url=url)
        chunks = self.chunker.chunk(content, anchors=anchors)
        logger.info("html_chunked", url=url, num_chunks=len(chunks))
        
        # Emit chunks with metadata
        metadata = {
            "content_type": "text/html",
            "extracted_by": "llm+readability",
            "llm_model": self.llm_extractor_cfg.get("model"),
            "language": doc.get("language", "unknown"),
            "sections_count": len(doc.get("sections", [])),
        }
        
        logger.info("html_emit_start", url=url)
        self.emitter.emit_chunks(
            chunks=chunks,
            source_url=url,
            source_file="",
            anchors=anchors,
            metadata=metadata,
        )
        logger.info("html_ingest_complete", url=url)
        
        return {"ok": True, "next_type": "none", "next_url": None}
    
    def _ingest_fallback(
        self,
        url: str,
        title: Optional[str],
        html: str,
    ) -> Dict[str, Any]:
        """Fallback HTML ingestion without LLM (readability only)."""
        
        logger.info("html_extract_start", url=url)
        bundle = clean_html_to_excerpt(html, url, self.max_chars)
        content = bundle["excerpt"]
        anchors = bundle["anchors_struct"]
        
        logger.info("html_extracted", url=url, content_length=len(content))
        
        if len(content) < self.min_content_length:
            logger.warning(
                "html_content_too_short",
                url=url,
                length=len(content),
                min_required=self.min_content_length,
            )
            return {"ok": False, "next_type": "none", "next_url": None}
        
        # Chunk content
        logger.info("html_chunking_start", url=url)
        chunks = self.chunker.chunk(content, anchors=anchors if anchors else None)
        logger.info("html_chunked", url=url, num_chunks=len(chunks))
        
        # Emit
        metadata = {
            "content_type": "text/html",
            "extracted_by": "readability",
        }
        
        logger.info("html_emit_start", url=url)
        self.emitter.emit_chunks(
            chunks=chunks,
            source_url=url,
            source_file="",
            anchors=anchors if anchors else None,
            metadata=metadata,
        )
        logger.info("html_ingest_complete", url=url)
        
        return {"ok": True, "next_type": "none", "next_url": None}


```

## [43] pipelines/executors/pdf_ingestor.py

```python
# FILE: pipelines/executors/pdf_ingestor.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\executors\pdf_ingestor.py
# NOTE: Concatenated snapshot for review
"""PDF document ingestor with LLM-guided chunking."""

import structlog
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pdfplumber
import requests
from pypdf import PdfReader
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic.llm import LLMClient
from agentic.normalize import extract_domain
from ingestion.anchors import AnchorDetector
from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter

logger = structlog.get_logger()


class PDFIngestor:
    """Ingest PDF documents with intelligent chunking."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        llm_client: LLMClient,
        chunker: TokenAwareChunker,
        emitter: JSONLEmitter,
    ):
        """
        Initialize PDF ingestor.
        
        Args:
            config: Ingest configuration
            llm_client: LLM client for marker suggestions
            chunker: Token-aware chunker
            emitter: Output emitter
        """
        self.config = config
        self.llm = llm_client
        self.chunker = chunker
        self.emitter = emitter
        self.download_dir = Path(config["download"]["download_dir"])
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = config["download"]["timeout"]
        self.user_agent = config["download"]["user_agent"]
        self.max_pages_preview = config["pdf"]["max_pages_preview"]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def download(
        self,
        url: str,
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
    ) -> Optional[Path]:
        """
        Download PDF with conditional requests.
        
        Args:
            url: PDF URL
            etag: Previous ETag for conditional request
            last_modified: Previous Last-Modified for conditional request
            
        Returns:
            Path to downloaded file, or None if not modified
        """
        headers = {"User-Agent": self.user_agent}
        
        # Conditional headers
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
        
        # Not modified
        if response.status_code == 304:
            return None
        
        response.raise_for_status()
        
        # Save to file
        filename = f"{hash(url)}.pdf"
        file_path = self.download_dir / filename
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return file_path
    
    def extract_text(self, pdf_path: Path) -> List[str]:
        """
        Extract text from PDF pages.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of page texts
        """
        pages = []
        
        try:
            # Try pdfplumber first
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    pages.append(text)
        except Exception:
            # Fallback to pypdf
            if self.config["pdf"]["fallback_to_pypdf"]:
                try:
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        text = page.extract_text() or ""
                        pages.append(text)
                except Exception:
                    pass
        
        return pages
    
    def ingest(
        self,
        url: str,
        title: Optional[str],
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        expected_type: str = "pdf",
    ) -> bool:
        """
        Ingest PDF document.
        
        Args:
            url: PDF URL
            title: Document title
            etag: Previous ETag
            last_modified: Previous Last-Modified
            expected_type: Expected document type (should be 'pdf')
            
        Returns:
            True if successfully ingested
        """
        # Validate expected type
        if expected_type and expected_type != "pdf":
            logger.error(
                "pdf_type_mismatch",
                url=url,
                expected=expected_type,
                executor="pdf",
            )
            return False
        
        try:
            # Download
            logger.info("pdf_download_start", url=url)
            pdf_path = self.download(url, etag, last_modified)
            
            if pdf_path is None:
                # Not modified, skip
                logger.info("pdf_not_modified", url=url)
                return False
            
            logger.info("pdf_downloaded", url=url, path=str(pdf_path))
            
            # Extract text
            logger.info("pdf_extract_start", url=url)
            pages = self.extract_text(pdf_path)
            
            if not pages:
                logger.warning("pdf_no_text_extracted", url=url)
                return False
            
            logger.info("pdf_extracted", url=url, num_pages=len(pages))
            
            # Get LLM marker suggestions
            logger.info("pdf_markers_start", url=url)
            domain = extract_domain(url)
            pages_preview = pages[:self.max_pages_preview]
            
            markers = self.llm.suggest_pdf_markers(
                title=title or url,
                pages_preview=pages_preview,
                domain=domain,
            )
            logger.info("pdf_markers_received", url=url, num_markers=len(markers) if markers else 0)
            
            # Detect anchors and segment
            logger.info("pdf_chunking_start", url=url)
            full_text = "\n\n".join(pages)
            
            if markers:
                detector = AnchorDetector(markers)
                segments = detector.segment_by_anchors(full_text)
                chunks = self.chunker.chunk_with_anchors(segments)
            else:
                # No markers, just chunk directly
                chunks = self.chunker.chunk(full_text)
            
            logger.info("pdf_chunked", url=url, num_chunks=len(chunks))
            
            # Emit chunks
            logger.info("pdf_emit_start", url=url)
            self.emitter.emit_chunks(
                chunks=chunks,
                source_url=url,
                source_file=str(pdf_path),
            )
            logger.info("pdf_ingest_complete", url=url)
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(
                "pdf_download_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "pdf_ingest_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise


```

## [44] pipelines/executors/zip_ingestor.py

```python
# FILE: pipelines/executors/zip_ingestor.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\executors\zip_ingestor.py
# NOTE: Concatenated snapshot for review
"""ZIP archive ingestor with table detection."""

import structlog
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter

logger = structlog.get_logger()


class ZIPIngestor:
    """Ingest ZIP archives containing regulatory tables."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        chunker: TokenAwareChunker,
        emitter: JSONLEmitter,
    ):
        """
        Initialize ZIP ingestor.
        
        Args:
            config: Ingest configuration
            chunker: Token-aware chunker
            emitter: Output emitter
        """
        self.config = config
        self.chunker = chunker
        self.emitter = emitter
        self.download_dir = Path(config["download"]["download_dir"])
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = config["download"]["timeout"]
        self.user_agent = config["download"]["user_agent"]
        self.max_extract_size = config["zip"]["max_extract_size_mb"] * 1024 * 1024
        self.allowed_extensions = config["zip"]["allowed_extensions"]
        self.table_patterns = config["zip"]["table_patterns"]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def download(self, url: str) -> Path:
        """Download ZIP file."""
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
        response.raise_for_status()
        
        filename = f"{hash(url)}.zip"
        file_path = self.download_dir / filename
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return file_path
    
    def extract_and_process(self, zip_path: Path, url: str, title: Optional[str]) -> bool:
        """
        Extract ZIP and process contents.
        
        Args:
            zip_path: Path to ZIP file
            url: Source URL
            title: Document title
            
        Returns:
            True if successfully processed
        """
        extract_dir = self.download_dir / f"{zip_path.stem}_extracted"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Check total size
                total_size = sum(info.file_size for info in zf.infolist())
                
                if total_size > self.max_extract_size:
                    return False
                
                # Extract
                zf.extractall(extract_dir)
                
                # Process extracted files
                processed_any = False
                
                for file_path in extract_dir.rglob('*'):
                    if file_path.is_file():
                        # Check extension
                        if file_path.suffix.lower() in self.allowed_extensions:
                            # Process file
                            if self._process_file(file_path, url, title):
                                processed_any = True
                
                return processed_any
        
        except Exception:
            return False
    
    def _process_file(self, file_path: Path, source_url: str, title: Optional[str]) -> bool:
        """Process individual file from ZIP."""
        try:
            # For simplicity, process text files and CSV
            if file_path.suffix.lower() in ['.txt', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for table patterns
                is_table = any(pattern in content for pattern in self.table_patterns)
                
                # Chunk content
                metadata = {
                    "is_table": is_table,
                    "file_name": file_path.name,
                    "file_type": file_path.suffix,
                }
                
                chunks = self.chunker.chunk(content, metadata)
                
                # Emit
                self.emitter.emit_chunks(
                    chunks=chunks,
                    source_url=source_url,
                    source_file=str(file_path),
                )
                
                return True
        
        except Exception:
            pass
        
        return False
    
    def ingest(
        self,
        url: str,
        title: Optional[str],
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        expected_type: str = "zip",
    ) -> bool:
        """
        Ingest ZIP archive.
        
        Args:
            url: ZIP URL
            title: Document title
            etag: Previous ETag (unused for now)
            last_modified: Previous Last-Modified (unused for now)
            expected_type: Expected document type (should be 'zip')
            
        Returns:
            True if successfully ingested
        """
        # Validate expected type
        if expected_type and expected_type != "zip":
            logger.error(
                "zip_type_mismatch",
                url=url,
                expected=expected_type,
                executor="zip",
            )
            return False
        
        try:
            logger.info("zip_download_start", url=url)
            zip_path = self.download(url)
            logger.info("zip_downloaded", url=url, path=str(zip_path))
            
            logger.info("zip_extract_start", url=url)
            result = self.extract_and_process(zip_path, url, title)
            
            if result:
                logger.info("zip_ingest_complete", url=url)
            else:
                logger.warning("zip_ingest_no_files_processed", url=url)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(
                "zip_download_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "zip_ingest_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise


```

## [45] pipelines/ingest_pipeline.py

```python
# FILE: pipelines/ingest_pipeline.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\ingest_pipeline.py
# NOTE: Concatenated snapshot for review
"""Ingest pipeline: read DB → diff → route → ingest."""

import argparse
import structlog
from typing import Any, Dict, List

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from agentic.llm import LLMClient
from common.env_readers import load_yaml_with_env

# Load .env into os.environ
load_dotenv()
from db.dao import DocumentCatalogDAO
from db.models import DocumentCatalog
from db.session import DatabaseSession
from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter
from pipelines.executors.html_ingestor import HTMLIngestor
from pipelines.executors.pdf_ingestor import PDFIngestor
from pipelines.executors.zip_ingestor import ZIPIngestor
from pipelines.routers import DocumentRouter

logger = structlog.get_logger()


class IngestPipeline:
    """Execute ingest pipeline: diff → route → process → emit."""
    
    def __init__(self, ingest_config: Dict[str, Any], db_config: Dict[str, Any]):
        """
        Initialize ingest pipeline.
        
        Args:
            ingest_config: Ingest configuration from ingest.yaml
            db_config: DB configuration from db.yaml
        """
        self.ingest_config = ingest_config
        self.db_config = db_config
        
        # Initialize LLM
        self.llm = LLMClient(
            api_key=ingest_config["llm"]["api_key"],
            model=ingest_config["llm"]["model"],
            temperature=ingest_config["llm"]["temperature"],
            max_tokens=ingest_config["llm"]["max_tokens"],
            timeout=ingest_config["llm"]["timeout"],
        )
        
        # Initialize router
        self.router = DocumentRouter(self.llm)
        
        # Initialize chunker
        chunking_cfg = ingest_config["chunking"]
        self.chunker = TokenAwareChunker(
            min_tokens=chunking_cfg["min_tokens"],
            max_tokens=chunking_cfg["max_tokens"],
            overlap_tokens=chunking_cfg["overlap_tokens"],
            encoding=chunking_cfg["encoding"],
        )
        
        # Initialize emitter
        output_cfg = ingest_config["output"]
        output_path = f"{output_cfg['output_dir']}/{output_cfg['filename']}"
        self.emitter = JSONLEmitter(output_path)
        
        # Initialize executors
        self.pdf_ingestor = PDFIngestor(ingest_config, self.llm, self.chunker, self.emitter)
        self.zip_ingestor = ZIPIngestor(ingest_config, self.chunker, self.emitter)
        self.html_ingestor = HTMLIngestor(ingest_config, self.chunker, self.emitter, self.llm)
        
        self.db_session = DatabaseSession()
    
    def execute(self, limit: int = 100) -> Dict[str, int]:
        """
        Execute ingest pipeline.
        
        Args:
            limit: Max documents to process
            
        Returns:
            Stats dict with counts
        """
        logger.info("ingest_pipeline_start", limit=limit)
        
        stats = {
            "total": 0,
            "new": 0,
            "changed": 0,
            "same": 0,
            "success": 0,
            "failed": 0,
        }
        
        with next(self.db_session.get_session()) as session:
            # Get pending/changed documents
            documents = DocumentCatalogDAO.get_pending_or_changed(session, limit=limit)
            
            stats["total"] = len(documents)
            logger.info("documents_to_process", count=stats["total"])
            
            for doc in documents:
                # Determine if NEW or CHANGED
                if doc.ingest_status == "pending":
                    status = "NEW"
                    stats["new"] += 1
                else:
                    status = "CHANGED"
                    stats["changed"] += 1
                
                logger.info("processing_document", url=doc.canonical_url, status=status)
                
                # Route document (trust DB final_type first)
                doc_type = self.router.route_item(
                    url=doc.canonical_url,
                    content_type=doc.content_type,
                    title=doc.title,
                    snippet=None,
                    final_type=getattr(doc, 'final_type', None),
                )
                
                logger.info("routed", url=doc.canonical_url, type=doc_type)
                
                # Ingest based on type
                result = self._ingest_document(session, doc, doc_type)
                
                # Handle result (can be bool for PDF/ZIP or dict for HTML)
                if isinstance(result, dict):
                    success = result.get("ok", False)
                    next_type = result.get("next_type")
                    next_url = result.get("next_url")
                    
                    # If HTML detected a PDF wrapper, log it
                    if next_type == "pdf" and next_url:
                        logger.info(
                            "pdf_wrapper_reroute",
                            original_url=doc.canonical_url,
                            pdf_url=next_url,
                        )
                        # Could enqueue PDF for processing here
                        # For now, just mark as failed with note
                        stats["failed"] += 1
                        DocumentCatalogDAO.mark_ingested(
                            session,
                            doc.canonical_url,
                            status="failed",
                            error_message=f"PDF wrapper detected: {next_url}",
                        )
                    elif success:
                        stats["success"] += 1
                        DocumentCatalogDAO.mark_ingested(session, doc.canonical_url, status="completed")
                    else:
                        stats["failed"] += 1
                        DocumentCatalogDAO.mark_ingested(
                            session,
                            doc.canonical_url,
                            status="failed",
                            error_message="Ingestion failed",
                        )
                else:
                    # Legacy bool return (PDF/ZIP ingestors)
                    success = result
                    if success:
                        stats["success"] += 1
                        DocumentCatalogDAO.mark_ingested(session, doc.canonical_url, status="completed")
                    else:
                        stats["failed"] += 1
                        DocumentCatalogDAO.mark_ingested(
                            session,
                            doc.canonical_url,
                            status="failed",
                            error_message="Ingestion failed",
                        )
                
                session.commit()
        
        logger.info("ingest_pipeline_complete", stats=stats)
        
        return stats
    
    def _ingest_document(
        self,
        session: Session,
        doc: DocumentCatalog,
        doc_type: str,
    ) -> bool | Dict[str, Any]:
        """
        Ingest a single document.
        
        Args:
            session: DB session
            doc: DocumentCatalog record
            doc_type: Document type ('pdf', 'zip', 'html')
            
        Returns:
            True if successful
        """
        try:
            if doc_type == "pdf":
                return self.pdf_ingestor.ingest(
                    url=doc.canonical_url,
                    title=doc.title,
                    etag=doc.etag,
                    last_modified=doc.last_modified,
                    expected_type=doc_type,
                )
            elif doc_type == "zip":
                return self.zip_ingestor.ingest(
                    url=doc.canonical_url,
                    title=doc.title,
                    etag=doc.etag,
                    last_modified=doc.last_modified,
                    expected_type=doc_type,
                )
            elif doc_type == "html":
                return self.html_ingestor.ingest(
                    url=doc.canonical_url,
                    title=doc.title,
                    etag=doc.etag,
                    last_modified=doc.last_modified,
                    expected_type=doc_type,
                )
            else:
                logger.error("unknown_doc_type", url=doc.canonical_url, type=doc_type)
                return False
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(
                "ingest_error",
                url=doc.canonical_url,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=error_trace,
            )
            return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run ingest pipeline")
    parser.add_argument("--config", default="configs/ingest.yaml", help="Ingest config path")
    parser.add_argument("--db", default="configs/db.yaml", help="DB config path")
    parser.add_argument("--limit", type=int, default=None, help="Max documents to process (overrides config)")
    
    args = parser.parse_args()
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    
    # Load configs
    ingest_config = load_yaml_with_env(args.config)
    db_config = load_yaml_with_env(args.db)
    
    # Get limit from CLI or config
    limit = args.limit if args.limit is not None else ingest_config.get("pipeline", {}).get("limit", 100)
    
    # Run pipeline
    pipeline = IngestPipeline(ingest_config, db_config)
    stats = pipeline.execute(limit=limit)
    
    print(f"Ingest complete: {stats}")


if __name__ == "__main__":
    main()


```

## [46] pipelines/routers.py

```python
# FILE: pipelines/routers.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\routers.py
# NOTE: Concatenated snapshot for review
"""Intent routing for document types with DB-first strategy."""

import structlog
from typing import Any, Dict, Literal, Optional

import requests

from agentic.detect import detect_type
from agentic.llm import LLMClient

logger = structlog.get_logger()


class DocumentRouter:
    """Route documents to appropriate ingestor based on type."""
    
    def __init__(self, llm_client: LLMClient, timeout: int = 20):
        """
        Initialize router.
        
        Args:
            llm_client: LLM client for fallback routing
            timeout: HTTP request timeout
        """
        self.llm = llm_client
        self.timeout = timeout
    
    def route_item(
        self,
        url: str,
        content_type: Optional[str] = None,
        title: Optional[str] = None,
        snippet: Optional[str] = None,
        final_type: Optional[str] = None,
    ) -> Literal["pdf", "zip", "html", "unknown"]:
        """
        Route document to appropriate ingestor.
        
        Priority:
        1. Trust final_type from DB if in {pdf, zip, html}
        2. Re-detect live if unknown
        3. LLM fallback as last resort
        
        Args:
            url: Document URL
            content_type: Content-Type header (legacy)
            title: Document title
            snippet: Search snippet
            final_type: Pre-detected type from DB (pdf/zip/html/unknown)
            
        Returns:
            Document type: 'pdf', 'zip', 'html', or 'unknown'
        """
        # 1. Trust DB final_type if resolved
        if final_type and final_type in ("pdf", "zip", "html"):
            logger.debug("route_from_db", url=url, final_type=final_type)
            return final_type  # type: ignore
        
        # 2. Re-detect live if unknown or missing
        if final_type == "unknown" or not final_type:
            logger.debug("route_redetect", url=url)
            
            try:
                # HEAD request for headers
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                headers = dict(response.headers)
            except Exception as e:
                logger.warning("route_head_failed", url=url, error=str(e))
                headers = {}
            
            # Detect type
            typing_info = detect_type(url, headers, sniff_magic=True)
            detected = typing_info.get("final_type")
            
            if detected and detected in ("pdf", "zip", "html"):
                logger.info("route_redetected", url=url, final_type=detected)
                return detected  # type: ignore
        
        # 3. LLM fallback
        logger.debug("route_llm_fallback", url=url)
        llm_result = self.llm.route_fallback(
            title=title or "",
            snippet=snippet or "",
            url=url,
        )
        
        # Sanitize LLM output
        llm_result_clean = llm_result.strip().lower()
        
        if llm_result_clean in ("pdf", "zip", "html"):
            logger.info("route_from_llm", url=url, final_type=llm_result_clean)
            return llm_result_clean  # type: ignore
        else:
            logger.warning("route_llm_invalid", url=url, llm_output=llm_result)
            # Default to html for unknown (most common on web)
            return "html"


```

## [47] pipelines/search_pipeline.py

```python
# FILE: pipelines/search_pipeline.py
# FULL: C:\Projetos\agentic-reg-ingest\pipelines\search_pipeline.py
# NOTE: Concatenated snapshot for review
"""Search pipeline: CSE → score → rank → persist."""

import argparse
import hashlib
import structlog
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from agentic.cse_client import CSEClient
from agentic.detect import detect_type, _url_ext
from agentic.normalize import extract_domain, normalize_url
from agentic.scoring import ResultScorer
from common.env_readers import load_yaml_with_env
from db.dao import DocumentCatalogDAO, SearchQueryDAO, SearchResultDAO
from db.session import DatabaseSession

# Load .env into os.environ
load_dotenv()

logger = structlog.get_logger()


class SearchPipeline:
    """Execute search pipeline: CSE → rank → cache."""
    
    def __init__(self, cse_config: Dict[str, Any], db_config: Dict[str, Any]):
        """
        Initialize search pipeline.
        
        Args:
            cse_config: CSE configuration from cse.yaml
            db_config: DB configuration from db.yaml
        """
        self.cse_config = cse_config
        self.db_config = db_config
        
        # Initialize clients
        self.cse = CSEClient(
            api_key=cse_config["api_key"],
            cx=cse_config["cx"],
            timeout=int(cse_config["timeout_seconds"]),
        )
        
        self.scorer = ResultScorer(cse_config)
        self.db_session = DatabaseSession()
        self.ttl_days = int(db_config.get("ttl_days", 7))
    
    def build_cache_key(
        self,
        cx: str,
        query: str,
        allow_domains: Optional[List[str]],
        topn: int,
    ) -> str:
        """Build cache key from search parameters."""
        allow_str = "|".join(sorted(allow_domains or []))
        cache_str = f"{cx}|{query}|{allow_str}|{topn}"
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get content metadata via HEAD request with typing detection.
        
        Args:
            url: Document URL
            
        Returns:
            Dict with content_type, last_modified, headers, and typing info
        """
        try:
            response = requests.head(
                url,
                timeout=int(self.cse_config["timeout_seconds"]),
                allow_redirects=True,
            )
            
            content_type = response.headers.get("Content-Type")
            last_modified_str = response.headers.get("Last-Modified")
            
            last_modified = None
            if last_modified_str:
                try:
                    last_modified = datetime.strptime(
                        last_modified_str,
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )
                except Exception:
                    pass
            
            # Detect document type
            typing_info = detect_type(url, dict(response.headers), sniff_magic=True)
            
            logger.debug(
                "metadata_fetched",
                url=url,
                final_type=typing_info.get("final_type"),
                fetch_status=typing_info.get("fetch_status"),
            )
            
            return {
                "content_type": content_type,
                "last_modified": last_modified,
                "headers": dict(response.headers),
                "typing": typing_info,
            }
        
        except Exception as e:
            logger.warning("metadata_fetch_failed", url=url, error=str(e))
            # Still try to detect from URL alone
            typing_info = detect_type(url, {}, sniff_magic=False)
            typing_info["fetch_status"] = "error"
            
            return {
                "content_type": None,
                "last_modified": None,
                "headers": {},
                "typing": typing_info,
            }
    
    def execute(
        self,
        query: str,
        allow_domains: Optional[List[str]] = None,
        topn: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Execute search pipeline.
        
        Args:
            query: Search query
            allow_domains: Optional domain whitelist
            topn: Max results to retrieve
            
        Returns:
            List of approved search results
        """
        cx = self.cse_config["cx"]
        cache_key = self.build_cache_key(cx, query, allow_domains, topn)
        
        logger.info("search_pipeline_start", query=query, cache_key=cache_key)
        
        # Check cache
        with next(self.db_session.get_session()) as session:
            cached_query = SearchQueryDAO.find_by_cache_key(session, cache_key)
            
            if cached_query and SearchQueryDAO.is_cache_valid(cached_query):
                logger.info("cache_hit", cache_key=cache_key)
                approved = SearchResultDAO.get_approved_results(session, cached_query.id)
                
                return [
                    {
                        "url": r.url,
                        "title": r.title,
                        "snippet": r.snippet,
                        "score": float(r.score) if r.score else 0.0,
                        "content_type": r.content_type,
                    }
                    for r in approved
                ]
            
            logger.info("cache_miss", cache_key=cache_key)
            
            # Execute CSE search
            items = self.cse.search_all(
                query=query,
                max_results=topn,
                results_per_page=int(self.cse_config["results_per_page"]),
            )
            
            logger.info("cse_results", count=len(items))
            
            # Score and rank
            scored_results = []
            
            for idx, item in enumerate(items):
                url = item.get("link", "")
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                
                # Normalize URL
                canonical_url = normalize_url(url)
                
                # Get metadata
                metadata = self.get_metadata(canonical_url)
                
                # Score
                score = self.scorer.score(
                    url=canonical_url,
                    title=title,
                    snippet=snippet,
                    content_type=metadata["content_type"],
                    last_modified=metadata["last_modified"],
                )
                
                typing_info = metadata.get("typing", {})
                headers = metadata.get("headers", {})
                
                scored_results.append({
                    "url": canonical_url,
                    "title": title,
                    "snippet": snippet,
                    "rank_position": idx + 1,
                    "score": score,
                    "content_type": metadata["content_type"],
                    "last_modified": metadata["last_modified"],
                    # Typing fields
                    "http_content_type": headers.get("Content-Type"),
                    "http_content_disposition": headers.get("Content-Disposition"),
                    "url_ext": _url_ext(canonical_url),
                    "detected_mime": typing_info.get("detected_mime"),
                    "detected_ext": typing_info.get("detected_ext"),
                    "final_type": typing_info.get("final_type", "unknown"),
                    "fetch_status": typing_info.get("fetch_status"),
                })
            
            # Sort by score descending
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            
            # Persist to database
            self._persist_results(session, cache_key, cx, query, allow_domains, topn, scored_results)
            
            logger.info("search_pipeline_complete", results_count=len(scored_results))
            
            return scored_results
    
    def _persist_results(
        self,
        session: Session,
        cache_key: str,
        cx: str,
        query: str,
        allow_domains: Optional[List[str]],
        topn: int,
        results: List[Dict[str, Any]],
    ) -> None:
        """Persist search results to database."""
        # Create/update search_query
        allow_str = "|".join(allow_domains) if allow_domains else None
        
        query_record = SearchQueryDAO.create(
            session,
            cache_key=cache_key,
            cx=cx,
            query_text=query,
            allow_domains=allow_str,
            top_n=topn,
            ttl_days=self.ttl_days,
        )
        
        # Create search_result records
        for result in results:
            SearchResultDAO.create(
                session,
                query_id=query_record.id,
                url=result["url"],
                title=result["title"],
                snippet=result["snippet"],
                rank_position=result["rank_position"],
                score=result["score"],
                content_type=result["content_type"],
                last_modified=result["last_modified"],
                approved=True,
                # Typing fields
                http_content_type=result.get("http_content_type"),
                http_content_disposition=result.get("http_content_disposition"),
                url_ext=result.get("url_ext"),
                detected_mime=result.get("detected_mime"),
                detected_ext=result.get("detected_ext"),
                final_type=result.get("final_type", "unknown"),
                fetch_status=result.get("fetch_status"),
            )
            
            # Upsert document_catalog
            domain = extract_domain(result["url"])
            
            DocumentCatalogDAO.upsert(
                session,
                canonical_url=result["url"],
                content_type=result["content_type"],
                last_modified=result["last_modified"],
                title=result["title"],
                domain=domain,
                final_type=result.get("final_type", "unknown"),
            )
        
        session.commit()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run search pipeline")
    parser.add_argument("--config", default="configs/cse.yaml", help="CSE config path")
    parser.add_argument("--db", default="configs/db.yaml", help="DB config path")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--topn", type=int, default=100, help="Max results")
    
    args = parser.parse_args()
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    
    # Load configs
    cse_config = load_yaml_with_env(args.config)
    db_config = load_yaml_with_env(args.db)
    
    # Run pipeline
    pipeline = SearchPipeline(cse_config, db_config)
    results = pipeline.execute(query=args.query, topn=args.topn)
    
    print(f"Found {len(results)} results")
    for r in results[:10]:
        print(f"  [{r['score']:.2f}] {r['title']}")


if __name__ == "__main__":
    main()


```

## [48] pyproject.toml

```toml
# FILE: pyproject.toml
# FULL: C:\Projetos\agentic-reg-ingest\pyproject.toml
# NOTE: Concatenated snapshot for review
[project]
name = "agentic-reg-ingest"
version = "1.0.0"
description = "Production-grade pipeline for searching and ingesting regulatory documents"
readme = "README.md"
requires-python = ">=3.11"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --strict-markers --tb=short"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true


```

## [49] requirements.in

```
// FILE: requirements.in
// FULL: C:\Projetos\agentic-reg-ingest\requirements.in
// NOTE: Concatenated snapshot for review
# Web Framework
fastapi
uvicorn[standard]

# HTTP Client
requests
httpx

# Data & Config
PyYAML
pydantic-settings
python-dotenv

# Logging & Utilities
structlog
tenacity
tqdm

# Database
sqlalchemy
pymysql
cryptography

# PDF Processing
pdfplumber
pypdf

# AI/LLM
openai

# Vector DB (optional)
qdrant-client

# Development Tools
ruff
black
mypy
pytest
pytest-asyncio
types-PyYAML
types-requests


```

## [50] requirements.txt

```text
# FILE: requirements.txt
# FULL: C:\Projetos\agentic-reg-ingest\requirements.txt
# NOTE: Concatenated snapshot for review
# Generated from requirements.in
# To update: pip-compile requirements.in

annotated-types==0.7.0
anyio==4.6.2.post1
beautifulsoup4==4.12.3
black==24.10.0
certifi==2024.8.30
cffi==1.17.1
charset-normalizer==3.4.0
click==8.1.7
colorama==0.4.6
cryptography==43.0.3
distro==1.9.0
lxml==5.3.0
fastapi==0.115.5
greenlet==3.1.1
grpcio==1.68.0
grpcio-tools==1.68.0
h11==0.14.0
httpcore==1.0.7
httptools==0.6.4
httpx==0.27.2
idna==3.10
jiter==0.7.1
mypy==1.13.0
mypy-extensions==1.0.0
openai==1.54.5
packaging==24.2
pathspec==0.12.1
pdfplumber==0.11.4
pillow==11.0.0
platformdirs==4.3.6
portalocker==2.10.1
protobuf==5.28.3
pycparser==2.22
pydantic==2.10.2
pydantic-core==2.27.1
pydantic-settings==2.6.1
pymysql==1.1.1
pypdf==5.1.0
pypdfium2==4.30.0
pytest==8.3.3
pytest-asyncio==0.24.0
python-dotenv==1.0.1
pyyaml==6.0.2
qdrant-client==1.12.1
requests==2.32.3
ruff==0.8.0
sniffio==1.3.1
sqlalchemy==2.0.36
starlette==0.41.3
structlog==24.4.0
tenacity==9.0.0
tiktoken==0.8.0
tqdm==4.67.0
trafilatura==1.12.2
types-pyyaml==6.0.12.20240917
types-requests==2.32.0.20241016
typing-extensions==4.12.2
urllib3==2.2.3
uvicorn==0.32.1
watchfiles==0.24.0
websockets==14.1


```

## [51] run_agentic.bat

```bat
// FILE: run_agentic.bat
// FULL: C:\Projetos\agentic-reg-ingest\run_agentic.bat
// NOTE: Concatenated snapshot for review
@echo off
REM Agentic Search Runner - Windows Wrapper
REM Usage: run_agentic.bat "seu prompt aqui"

if "%~1"=="" (
    echo.
    echo ========================================
    echo   Agentic Search - Quick Runner
    echo ========================================
    echo.
    echo Usage:
    echo   run_agentic.bat "Buscar RNs da ANS sobre prazos de atendimento"
    echo.
    echo Options:
    echo   run_agentic.bat --example       Run with example plan
    echo   run_agentic.bat --view PLAN_ID  View iterations
    echo   run_agentic.bat --help          Show full help
    echo.
    exit /b 1
)

if "%~1"=="--example" (
    echo Running with example plan...
    .venv\Scripts\python.exe scripts\run_agentic.py --plan-file examples\agentic_plan_example.json --debug
    exit /b 0
)

if "%~1"=="--view" (
    if "%~2"=="" (
        echo Error: PLAN_ID required
        echo Usage: run_agentic.bat --view PLAN_ID
        exit /b 1
    )
    .venv\Scripts\python.exe scripts\view_agentic_iters.py %2
    exit /b 0
)

if "%~1"=="--help" (
    .venv\Scripts\python.exe scripts\run_agentic.py --help
    exit /b 0
)

REM Run with prompt
echo.
echo ========================================
echo   Agentic Search Starting...
echo ========================================
echo.
.venv\Scripts\python.exe scripts\run_agentic.py --prompt "%~1" --debug

exit /b %ERRORLEVEL%


```

## [52] vector/__init__.py

```python
# FILE: vector/__init__.py
# FULL: C:\Projetos\agentic-reg-ingest\vector\__init__.py
# NOTE: Concatenated snapshot for review
"""Vector database utilities."""


```

## [53] vector/qdrant_loader.py

```python
# FILE: vector/qdrant_loader.py
# FULL: C:\Projetos\agentic-reg-ingest\vector\qdrant_loader.py
# NOTE: Concatenated snapshot for review
"""Load JSONL chunks into Qdrant vector database."""

import argparse
import json
import structlog
from pathlib import Path
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from common.env_readers import load_yaml_with_env

logger = structlog.get_logger()


class QdrantLoader:
    """Load document chunks into Qdrant."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Qdrant loader.
        
        Args:
            config: Configuration from settings.yaml
        """
        self.config = config
        
        # Initialize client
        url = config["url"]
        api_key = config.get("api_key", "")
        
        self.client = QdrantClient(url=url, api_key=api_key if api_key else None)
        
        self.collection_name = config["collection"]["name"]
        self.vector_size = config["collection"]["vector_size"]
        self.distance = self._get_distance_metric(config["collection"]["distance"])
        self.batch_size = config.get("batch_size", 100)
    
    def _get_distance_metric(self, distance_str: str) -> Distance:
        """Convert distance string to Qdrant Distance enum."""
        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclidean": Distance.EUCLID,
            "Dot": Distance.DOT,
        }
        return distance_map.get(distance_str, Distance.COSINE)
    
    def ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            logger.info("creating_collection", name=self.collection_name)
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance,
                ),
            )
        else:
            logger.info("collection_exists", name=self.collection_name)
    
    def load_jsonl(self, jsonl_path: Path) -> List[Dict[str, Any]]:
        """
        Load chunks from JSONL file.
        
        Args:
            jsonl_path: Path to JSONL file
            
        Returns:
            List of chunk records
        """
        chunks = []
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        For production, use sentence-transformers or OpenAI embeddings.
        This is a placeholder that returns a zero vector.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        # TODO: Replace with actual embedding model
        # Example with sentence-transformers:
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer(self.config["collection"]["embedding_model"])
        # return model.encode(text).tolist()
        
        # Placeholder: return zero vector
        return [0.0] * self.vector_size
    
    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Upsert chunks into Qdrant.
        
        Args:
            chunks: List of chunk records from JSONL
        """
        logger.info("upserting_chunks", count=len(chunks))
        
        points = []
        
        for idx, chunk in enumerate(chunks):
            # Generate embedding
            text = chunk["text"]
            embedding = self.generate_embedding(text)
            
            # Create point
            point = PointStruct(
                id=idx,  # In production, use UUID or hash
                vector=embedding,
                payload={
                    "text": text,
                    "source_url": chunk.get("source_url", ""),
                    "source_file": chunk.get("source_file", ""),
                    "chunk_index": chunk.get("chunk_index", 0),
                    "total_chunks": chunk.get("total_chunks", 1),
                    "anchor_type": chunk.get("anchor_type"),
                    "anchor_text": chunk.get("anchor_text"),
                },
            )
            
            points.append(point)
            
            # Batch upsert
            if len(points) >= self.batch_size:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
                points = []
        
        # Upsert remaining
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
        
        logger.info("upsert_complete")
    
    def load_from_file(self, jsonl_path: Path) -> None:
        """
        Load chunks from JSONL file into Qdrant.
        
        Args:
            jsonl_path: Path to JSONL file
        """
        # Ensure collection exists
        self.ensure_collection()
        
        # Load chunks
        chunks = self.load_jsonl(jsonl_path)
        logger.info("loaded_chunks", count=len(chunks))
        
        # Upsert
        self.upsert_chunks(chunks)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Load chunks into Qdrant")
    parser.add_argument("--config", default="vector/settings.yaml", help="Qdrant config path")
    parser.add_argument("--input", required=True, help="JSONL input file")
    
    args = parser.parse_args()
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    
    # Load config
    config = load_yaml_with_env(args.config)
    
    # Load into Qdrant
    loader = QdrantLoader(config)
    loader.load_from_file(Path(args.input))
    
    print(f"Loaded chunks from {args.input} into Qdrant")


if __name__ == "__main__":
    main()


```

## [54] vector/settings.yaml

```yaml
# FILE: vector/settings.yaml
# FULL: C:\Projetos\agentic-reg-ingest\vector\settings.yaml
# NOTE: Concatenated snapshot for review
# Qdrant Vector Database Settings

url: ${QDRANT_URL}
api_key: ${QDRANT_API_KEY}

collection:
  name: ${QDRANT_COLLECTION}
  vector_size: 384
  distance: Cosine
  
  # Embedding model (sentence-transformers)
  embedding_model: all-MiniLM-L6-v2

# Batch processing
batch_size: 100


```
