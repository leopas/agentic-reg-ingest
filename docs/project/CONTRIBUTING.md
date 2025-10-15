<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Contributing Guide

Guia completo para contribuidores.

## ✨ Como Contribuir

### 1. Fork & Setup
```bash
git fork https://github.com/original/agentic-reg-ingest
git clone https://github.com/yourusername/agentic-reg-ingest
cd agentic-reg-ingest

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Create Branch
```bash
git checkout -b feat/my-feature
# or
git checkout -b fix/bug-name
```

### 3. Make Changes

**Obrigatório:**
- ✅ Add SPDX header to new files:
  ```python
  # SPDX-License-Identifier: MIT
  # Copyright (c) 2025 Leopoldo Carvalho Correia de Lima
  ```
- ✅ Write tests
- ✅ Update docs
- ✅ Follow code style

### 4. Test
```bash
make test          # Run tests
make lint          # Code formatting
make typecheck     # Type checking
```

### 5. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(rag): add streaming responses
fix(vector): correct point ID generation
docs(api): update endpoint examples
chore(deps): bump fastapi to 0.105.0
```

### 6. Push & PR
```bash
git push origin feat/my-feature
```

Abra PR no GitHub com:
- Descrição clara
- Link para issue (se aplicável)
- Screenshots (se UI)
- Update CHANGELOG.md

---

## 📋 Checklist para PR

- [ ] Tests passando
- [ ] Lint ok
- [ ] Type check ok
- [ ] SPDX headers em novos arquivos
- [ ] Docs atualizados
- [ ] CHANGELOG.md atualizado
- [ ] PR description completa

---

## 🎯 Áreas para Contribuir

- 🐛 Bug fixes
- ✨ New features
- 📖 Documentation
- 🧪 Tests
- 🎨 UI improvements
- ⚡ Performance optimization

---

[← Index](../index.md) | [Code of Conduct →](CODE_OF_CONDUCT.md)

