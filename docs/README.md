<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 📚 Documentação - agentic-reg-ingest

Documentação completa do projeto organizada por categoria.

## 📖 Estrutura

```
docs/
├── guides/           → Guias de uso do sistema
├── setup/            → Instalação e configuração
├── development/      → Desenvolvimento e debug
└── changelog/        → Histórico de mudanças
```

---

## 🚀 Começando

**Primeiro acesso?** → [docs/setup/START_HERE.md](setup/START_HERE.md)

**Setup completo?** → [docs/setup/SETUP_COMPLETO.md](setup/SETUP_COMPLETO.md)

**Quick start?** → [docs/setup/QUICKSTART_CHECKLIST.md](setup/QUICKSTART_CHECKLIST.md)

---

## 📋 Guias por Categoria

### 🎯 [Guides](guides/) - Guias de Uso

| Guia | Descrição |
|------|-----------|
| [AGENTIC_QUICKSTART](guides/AGENTIC_QUICKSTART.md) | Quick start para Agentic Search |
| [AGENTIC_CHEATSHEET](guides/AGENTIC_CHEATSHEET.md) | Comandos rápidos |
| [AGENTIC_CONFIG_GUIDE](guides/AGENTIC_CONFIG_GUIDE.md) | Configuração de planos |
| [AUDIT_TRAIL_GUIDE](guides/AUDIT_TRAIL_GUIDE.md) | Como interpretar audit trail |
| [CHAT_RAG_GUIDE](guides/CHAT_RAG_GUIDE.md) | Chat RAG com kb_regulatory |
| [VECTOR_PUSH_GUIDE](guides/VECTOR_PUSH_GUIDE.md) | Push de chunks para VectorDB |
| [UI_GUIDE](guides/UI_GUIDE.md) | Interface web (HTMX) |
| [QUICK_REFERENCE](guides/QUICK_REFERENCE.md) | Referência rápida |
| [QUICK_START_HTML](guides/QUICK_START_HTML.md) | HTML-only quick start |

### ⚙️ [Setup](setup/) - Instalação

| Guia | Descrição |
|------|-----------|
| [START_HERE](setup/START_HERE.md) | **Comece aqui** - Guia inicial |
| [SETUP_COMPLETO](setup/SETUP_COMPLETO.md) | Setup completo passo a passo |
| [SETUP_VECTOR_PUSH](setup/SETUP_VECTOR_PUSH.md) | Setup do Vector Push |
| [QUICKSTART_CHECKLIST](setup/QUICKSTART_CHECKLIST.md) | Checklist de setup |

### 🔧 [Development](development/) - Desenvolvimento

| Guia | Descrição |
|------|-----------|
| [DEBUG_GUIDE](development/DEBUG_GUIDE.md) | Como debugar o sistema |
| [DEBUG_WEB_UI](development/DEBUG_WEB_UI.md) | Debug da interface web |
| [TEST_AGENTIC](development/TEST_AGENTIC.md) | Testes do Agentic Search |
| [CONTRIBUTING](development/CONTRIBUTING.md) | Como contribuir |
| [IMPLEMENTATION_SUMMARY](development/IMPLEMENTATION_SUMMARY.md) | Resumo da implementação |
| [repo_concat_all](development/repo_concat_all.md) | Código concatenado |

### 📅 [Changelog](changelog/) - Histórico

| Arquivo | Descrição |
|---------|-----------|
| [CHANGELOG](changelog/CHANGELOG.md) | Changelog principal |
| [CHANGELOG_AGENTIC](changelog/CHANGELOG_AGENTIC.md) | Changelog do Agentic Search |

---

## 🎯 Guias por Tarefa

### Quero instalar o sistema
1. [START_HERE](setup/START_HERE.md) - Guia inicial
2. [SETUP_COMPLETO](setup/SETUP_COMPLETO.md) - Setup detalhado
3. [QUICKSTART_CHECKLIST](setup/QUICKSTART_CHECKLIST.md) - Checklist

### Quero usar Agentic Search
1. [AGENTIC_QUICKSTART](guides/AGENTIC_QUICKSTART.md) - Quick start
2. [AGENTIC_CHEATSHEET](guides/AGENTIC_CHEATSHEET.md) - Comandos rápidos
3. [AGENTIC_CONFIG_GUIDE](guides/AGENTIC_CONFIG_GUIDE.md) - Configuração

### Quero usar RAG Chat
1. [CHAT_RAG_GUIDE](guides/CHAT_RAG_GUIDE.md) - Guia completo do Chat
2. URL: `http://localhost:8000/chat`

### Quero enviar chunks para VectorDB
1. [VECTOR_PUSH_GUIDE](guides/VECTOR_PUSH_GUIDE.md) - Guia de push
2. [SETUP_VECTOR_PUSH](setup/SETUP_VECTOR_PUSH.md) - Setup do vector

### Quero debugar problemas
1. [DEBUG_GUIDE](development/DEBUG_GUIDE.md) - Debug geral
2. [DEBUG_WEB_UI](development/DEBUG_WEB_UI.md) - Debug da UI

### Quero contribuir
1. [CONTRIBUTING](development/CONTRIBUTING.md) - Como contribuir
2. [TEST_AGENTIC](development/TEST_AGENTIC.md) - Como testar

---

## 🔗 Links Úteis

**URLs do Sistema:**
- Root: `http://localhost:8000/`
- Agentic Console: `http://localhost:8000/ui`
- RAG Chat: `http://localhost:8000/chat`
- API Docs: `http://localhost:8000/docs`

**Documentação Principal:**
- [README.md](../README.md) - Documentação principal (raiz)
- [LICENSE](../LICENSE) - Licença MIT

---

## 📊 Mapa Mental

```
📚 DOCS
│
├── 🚀 SETUP
│   ├── Primeira vez? → START_HERE
│   ├── Detalhado? → SETUP_COMPLETO
│   └── Checklist? → QUICKSTART_CHECKLIST
│
├── 📖 GUIDES
│   ├── Agentic Search → AGENTIC_*
│   ├── RAG Chat → CHAT_RAG_GUIDE
│   ├── Vector DB → VECTOR_PUSH_GUIDE
│   └── Interface → UI_GUIDE
│
├── 🔧 DEVELOPMENT
│   ├── Debug → DEBUG_*
│   ├── Tests → TEST_AGENTIC
│   └── Contribute → CONTRIBUTING
│
└── 📅 CHANGELOG
    └── Histórico completo
```

---

**Built with ❤️ by Leopoldo Carvalho Correia de Lima**

