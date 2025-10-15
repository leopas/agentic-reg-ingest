<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Retention Policy

Política de retenção de dados.

## ⏰ Prazos por Tipo

| Tipo de Dado | Retenção | Justificativa |
|--------------|----------|---------------|
| Search cache | 30 dias (TTL) | Evitar queries duplicadas |
| Chunks (cache) | 180 dias | Re-processamento diff |
| Vector points | 365 dias+ | Knowledge base perene |
| Audit trail | 365 dias+ | Compliance |

## 🗑️ Deleção

```bash
# Manual cleanup (se necessário)
mysql -e "DELETE FROM search_query WHERE expires_at < NOW()"

# Vector cleanup (por doc_hash)
curl -X POST http://localhost:8000/vector/delete \
  -d '{"doc_hashes":["abc"], "collection":"kb_regulatory"}'
```

---

[← Privacy](PRIVACY_TELEMETRY.md)

