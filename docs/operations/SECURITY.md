<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Security

Práticas de segurança e mitigações de riscos.

## 🔒 Threat Model

### Ameaças Identificadas

**1. Injection via Malicious Documents**
- **Vetor:** HTML/PDF com scripts, SQL injection em títulos
- **Impacto:** XSS, code execution
- **Mitigação:**
  - ✅ HTML sanitization (readability, trafilatura)
  - ✅ PDF parsing seguro (pdfplumber, sem eval)
  - ✅ Parameterized SQL (SQLAlchemy ORM)
  - ✅ Escape de payload no Qdrant

**2. API Abuse**
- **Vetor:** Excesso de queries (DoS), custos elevados
- **Impacto:** Bill shock, quota exceeded
- **Mitigação:**
  - ✅ Rate limiting (FastAPI middleware)
  - ✅ Budget configs (max_cse_calls)
  - ✅ Authentication (adicionar se público)

**3. Data Leakage**
- **Vetor:** Logs com PII, chunks sensíveis no VectorDB
- **Impacto:** LGPD violation
- **Mitigação:**
  - ✅ Allowlist de domínios (só públicos)
  - ✅ Deny patterns (URLs sensíveis)
  - ✅ Redact PII (se necessário)
  - ✅ Logs estruturados (sem dados sensíveis)

**4. Dependency Vulnerabilities**
- **Vetor:** CVEs em bibliotecas
- **Impacto:** RCE, data breach
- **Mitigação:**
  - ✅ Dependabot alerts
  - ✅ `pip-audit` em CI
  - ✅ Renovação mensal

---

## 🔐 Secrets Management

### Never Commit
- ❌ `.env` file
- ❌ API keys
- ❌ Passwords
- ❌ Tokens

### Recommendations
- ✅ Use `.env` (gitignored)
- ✅ Rotate keys regularly (90 dias)
- ✅ Least privilege (API scopes mínimos)
- ✅ Secrets manager em produção (AWS Secrets Manager, Azure Key Vault)

---

## 🛡️ Hardening

### API
- Add authentication (OAuth2/JWT)
- Rate limiting (slowapi)
- CORS configurável
- HTTPS only em produção

### Database
- Read-only user para queries
- Encrypted connections (TLS)
- Backups automáticos
- Audit log de alterações

### Vector DB
- API key para Qdrant
- Network isolation (VPC)
- Backup de collections

---

Ver também: [Privacy & Telemetry](PRIVACY_TELEMETRY.md)

[← Deployment](DEPLOYMENT_GUIDE.md) | [Observability →](OBSERVABILITY.md)

