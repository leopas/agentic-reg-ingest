<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

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

