<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Security Policy

## 🔒 Reporting a Vulnerability

**Do NOT** open a public issue for security vulnerabilities.

**Instead:**
1. Email: leopoldo.de.lima@gmail.com
2. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

**Response Time:**
- Initial response: 48 hours
- Assessment: 7 days
- Fix (if confirmed): 30 days

---

## 🛡️ Security Best Practices

Ver documentação completa: **[docs/operations/SECURITY.md](docs/operations/SECURITY.md)**

### For Operators

- ✅ Never commit `.env` files
- ✅ Rotate API keys regularly
- ✅ Use allow/deny lists
- ✅ Enable budget limits
- ✅ Monitor logs for anomalies

### For Developers

- ✅ Sanitize HTML inputs
- ✅ Validate all user inputs (Pydantic)
- ✅ Use parameterized SQL queries (SQLAlchemy ORM)
- ✅ Add SPDX headers to new files
- ✅ Run `pip-audit` before releasing

---

## 📋 Supported Versions

| Version | Supported |
|---------|-----------|
| 2.0.x   | ✅ Yes    |
| 1.x     | ⚠️ Best effort |
| < 1.0   | ❌ No     |

---

## 🔐 Known Issues

Currently: None

Check [GitHub Security Advisories](https://github.com/yourusername/agentic-reg-ingest/security/advisories) for updates.

---

**Security is a priority. Thank you for helping keep this project safe!** 🛡️

