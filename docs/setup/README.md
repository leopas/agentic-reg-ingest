<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# ⚙️ Setup - Installation & Configuration

Guias de instalação e configuração do sistema.

## 🚀 Por onde começar?

### 1️⃣ **Primeira vez?**
→ [START_HERE.md](START_HERE.md) - Guia inicial passo a passo

### 2️⃣ **Setup detalhado?**
→ [SETUP_COMPLETO.md](SETUP_COMPLETO.md) - Setup completo com troubleshooting

### 3️⃣ **Checklist rápido?**
→ [QUICKSTART_CHECKLIST.md](QUICKSTART_CHECKLIST.md) - Lista de verificação

### 4️⃣ **Configurar Vector Push?**
→ [SETUP_VECTOR_PUSH.md](SETUP_VECTOR_PUSH.md) - Setup de VectorDB e embeddings

---

## 📋 Guias Disponíveis

| Guia | O que cobre | Tempo estimado |
|------|-------------|----------------|
| **START_HERE** | Instalação básica, primeiro uso | 15 min |
| **SETUP_COMPLETO** | MySQL, Qdrant, OpenAI, migrations, testes | 30-45 min |
| **SETUP_VECTOR_PUSH** | Qdrant, embeddings, Python 3.12 | 20 min |
| **QUICKSTART_CHECKLIST** | Lista de verificação rápida | 5 min |

---

## ⚡ Quick Setup (TL;DR)

```bash
# 1. Clonar repo
git clone <repo>
cd agentic-reg-ingest

# 2. Python 3.12 (importante!)
python3.12 -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate (Windows)

# 3. Instalar deps
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Edite: MYSQL_*, OPENAI_*, QDRANT_*

# 5. Migrar DB
make db-init
make migrate
make migrate-agentic
make migrate-chunks

# 6. Iniciar Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# 7. Iniciar servidor
make api

# 8. Acessar UIs
# http://localhost:8000/ui    → Agentic Console
# http://localhost:8000/chat  → RAG Chat
```

---

## 🔑 Variáveis de Ambiente

### Obrigatórias

```bash
# MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=...
MYSQL_DB=agentic_reg_ingest

# OpenAI (para LLM e embeddings)
OPENAI_API_KEY=sk-proj-...

# Google CSE
CSE_API_KEY=...
CSE_CX=...
```

### Opcionais

```bash
# Qdrant (default: localhost)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Embeddings (defaults ok)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBED_DIM=1536

# LLM (defaults ok)
OPENAI_MODEL=gpt-4o-mini

# Cache TTL
TTL_DAYS=30
```

---

## 🐳 Docker Quick Start

```bash
# Qdrant
docker run -d -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --name qdrant \
  qdrant/qdrant

# MySQL (se não tiver local)
docker run -d -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=senha \
  -e MYSQL_DATABASE=agentic_reg_ingest \
  --name mysql \
  mysql:8.0
```

---

## ⚠️ Avisos Importantes

### Python 3.13 Incompatibilidade

**Problema:** SQLAlchemy 2.x incompatível com Python 3.13

**Solução:** Use Python **3.12**!

```bash
python3.12 -m venv .venv
```

### Dependências Faltantes

```bash
# Se der erro ao importar:
pip install pdfplumber pypdf trafilatura beautifulsoup4 lxml numpy
```

---

[← Voltar para docs](../README.md) | [README Principal](../../README.md)

