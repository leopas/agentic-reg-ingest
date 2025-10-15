<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 🔧 Development - Developer Resources

Recursos para desenvolvedores e contribuidores.

## 🐛 Debug

| Guia | Descrição | Quando usar |
|------|-----------|-------------|
| [DEBUG_GUIDE](DEBUG_GUIDE.md) | 🔍 Debug geral do sistema | Problemas no backend, pipelines |
| [DEBUG_WEB_UI](DEBUG_WEB_UI.md) | 🖥️ Debug da interface web | Problemas na UI, HTMX, JavaScript |

## 🧪 Testing

| Guia | Descrição | Quando usar |
|------|-----------|-------------|
| [TEST_AGENTIC](TEST_AGENTIC.md) | ✅ Testes do Agentic Search | Validar funcionalidades |

## 👥 Contributing

| Guia | Descrição | Quando usar |
|------|-----------|-------------|
| [CONTRIBUTING](CONTRIBUTING.md) | 🤝 Como contribuir | Antes de abrir PR |

## 📊 Implementation

| Guia | Descrição | Quando usar |
|------|-----------|-------------|
| [IMPLEMENTATION_SUMMARY](IMPLEMENTATION_SUMMARY.md) | 📝 Resumo da implementação | Entender arquitetura completa |
| [repo_concat_all](repo_concat_all.md) | 🗂️ Código concatenado | Visão geral do codebase |

---

## 🛠️ Comandos Úteis

### Testes

```bash
# Todos os testes
make test

# Testes específicos
pytest tests/test_chat_rag.py -v
pytest tests/test_vector_components.py -v
```

### Linting

```bash
# Black (formatação)
make lint

# Type checking
make typecheck
```

### Debug

```bash
# Com VSCode
# F5 → Selecione configuração

# Via CLI com logs detalhados
python scripts/run_agentic.py --debug --plan-only
```

---

## 📁 Estrutura do Projeto

```
agentic-reg-ingest/
├── apps/
│   ├── api/              # FastAPI endpoints
│   └── ui/               # HTMX frontends
├── agentic/              # Agentic search core
├── embeddings/           # Embedding generation
├── rag/                  # RAG components
├── pipelines/            # Search & Ingest pipelines
├── db/                   # Database ORM & DAOs
├── vector/               # Qdrant integration
├── ingestion/            # Chunking & emitting
├── common/               # Shared utilities
├── configs/              # YAML configurations
├── scripts/              # CLI scripts
├── tests/                # Test suite
└── docs/                 # Documentation ← VOCÊ ESTÁ AQUI
```

---

## 🎯 Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────┐
│                   WEB UIs (HTMX)                        │
│  /ui (Agentic Console)  |  /chat (RAG Chat)            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│              FastAPI REST API                           │
│  /agentic/*  |  /chat/*  |  /vector/*  |  /ingest/*   │
└────────────────┬────────────────────────────────────────┘
                 │
      ┌──────────┼──────────┬──────────┐
      │          │          │          │
┌─────▼──┐  ┌───▼───┐  ┌──▼────┐  ┌─▼──────┐
│ Search │  │ RAG   │  │Vector │  │Database│
│Pipeline│  │Engine │  │ DB    │  │(MySQL) │
└────────┘  └───────┘  └───────┘  └────────┘
   CSE       Qdrant     Qdrant      Models
            +OpenAI    +Embeddings   +DAOs
```

---

## 🔐 Código de Conduta

- Respeite as licenças (MIT)
- Siga SPDX headers
- Escreva testes para novas features
- Documente mudanças
- Use type hints
- Mantenha estrutlog para logs

---

## 📝 Checklist para PRs

- [ ] Código com SPDX header
- [ ] Testes passando (`make test`)
- [ ] Lint ok (`make lint`)
- [ ] Type check ok (`make typecheck`)
- [ ] Migrations (se aplicável)
- [ ] Documentação atualizada
- [ ] Changelog atualizado

---

[← Voltar para docs](../README.md) | [README Principal](../../README.md)

