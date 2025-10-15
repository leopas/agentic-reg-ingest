<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Anchors & Chunking Strategy

Ver implementação: `ingestion/chunkers.py` e `ingestion/anchors.py`

## Estratégia

1. **Detect anchors** (Art., Anexo, H1-H3)
2. **Segment** por anchors
3. **Token-aware split** (512 tokens, 50 overlap)
4. **Metadata enrichment**

---

[← RAG Evaluation](EVALUATION_PLAN.md)

