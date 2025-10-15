<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Endpoints Quickstart

Ver [API Reference](API_REFERENCE.md) para detalhes completos.

## ⚡ Sequência Típica

```bash
# 1. Gerar plano
curl -X POST http://localhost:8000/agentic/plan \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Buscar RNs ANS prazos"}'

# 2. Executar plano
curl -X POST http://localhost:8000/agentic/run \
  -d '{"plan_id":"550e..."}'

# 3. Listar aprovados
curl "http://localhost:8000/agentic/approved?limit=100"

# 4. Regenerar chunks
curl -X POST http://localhost:8000/ingest/regenerate \
  -d '{"urls":["https://..."], "overwrite":true}'

# 5. Push para vector
curl -X POST http://localhost:8000/vector/push \
  -d '{"doc_hashes":["abc"], "collection":"kb_regulatory"}'

# 6. Perguntar no chat
curl -X POST http://localhost:8000/chat/ask \
  -d '{"question":"Quais prazos?", "mode":"grounded"}'
```

---

[← API Reference](API_REFERENCE.md)

