<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Data Provenance

Rastreabilidade de fontes de dados.

## 📋 Fontes Oficiais

- www.gov.br/ans (ANS)
- www.planalto.gov.br (Legislação federal)
- Outros domínios governamentais (.gov.br)

## 🔍 Rastreabilidade

Cada chunk armazena:
- `url` - URL fonte
- `doc_hash` - Identificador único
- `last_modified` - Data da versão
- `etag` - Versionamento
- `approved_at` - Quando aprovado

Ver: `document_catalog` table e Qdrant payload.

---

[← Index](../index.md)

