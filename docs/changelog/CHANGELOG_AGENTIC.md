<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 📝 Changelog - Agentic Search Implementation

## [2.0.0] - 2025-10-14 - AGENTIC SEARCH RELEASE 🚀

### 🎉 **MEGA FEATURE: True Agentic Search**

Transformação completa do sistema de busca linear para **loop agentivo autônomo** com Plan→Act→Observe→Judge→Re-plan.

---

## ✨ **Added**

### **Agentic Search System**
- **LLM Planner** (`agentic/llm.py::plan_from_prompt()`) - Gera plano estruturado via prompt
- **LLM Judge** (`agentic/llm.py::judge_candidates()`) - Avalia candidatos semanticamente
- **Agentic Controller** (`pipelines/agentic_controller.py`) - Loop completo (550 linhas)
- **Pydantic Schemas** (`agentic/schemas.py`) - Models validados: Plan, Judge, Quality
- **Quality Gates** (`agentic/quality.py`) - Filtros multi-critério + anchor detection
- **Audit Tables** - `agentic_plan` e `agentic_iter` para compliance

### **CLI & Debug Tools**
- **CLI Runner** (`scripts/run_agentic.py`) - Interface completa com dry-run e debug mode
- **Iteration Viewer** (`scripts/view_agentic_iters.py`) - Visualizador de audit trail
- **VSCode Launch Config** (`.vscode/launch.json`) - 12 configurações de debug
- **Windows Wrapper** (`run_agentic.bat`) - Atalho simples
- **Linux/Mac Wrapper** (`scripts/run_agentic.sh`) - Atalho simples

### **API Endpoints**
- `POST /agentic/plan` - Criar plano via prompt
- `POST /agentic/run` - Executar loop agentivo
- `GET /agentic/iters/{plan_id}` - Ver audit trail

### **Configuration**
- **Agentic Config** (`configs/agentic.yaml`) - Defaults para stop/quality/budget
- **Example Plan** (`examples/agentic_plan_example.json`) - Plano pronto para usar

### **Documentation**
- **Quickstart Guide** (`AGENTIC_QUICKSTART.md`) - Tutorial completo
- **Cheat Sheet** (`AGENTIC_CHEATSHEET.md`) - Referência rápida
- **Test Guide** (`TEST_AGENTIC.md`) - Como testar e debugar
- **README Section** - Seção "Agentic Search" detalhada

### **Tests**
- `tests/test_agentic_plan.py` - Schema validation (8 tests)
- `tests/test_agentic_quality.py` - Quality gates (8 tests)

### **Makefile Targets**
- `make migrate-agentic` - Rodar migração agentic
- `make agentic-example` - Executar com plano exemplo
- `make agentic-view PLAN_ID=...` - Ver iterations

---

## 🔧 **Changed**

### **LLM Module**
- Extended `agentic/llm.py` with planner and judge methods (+210 lines)

### **Database**
- Extended `db/dao.py` with `AgenticPlanDAO` and `AgenticIterDAO` (+135 lines)
- Added `agentic_plan` and `agentic_iter` tables (migration)

### **API**
- Extended `apps/api/main.py` with 3 agentic endpoints (+185 lines)
- Added request/response models for agentic endpoints

### **Documentation**
- Updated `README.md` with comprehensive Agentic Search section (+230 lines)
- Updated `Makefile` help text

---

## 🐛 **Fixed**

### **Settings & Environment**
- Fixed `common/settings.py` to use `mysql_db` instead of `MYSQL_DATABASE`
- Updated all documentation to use `MYSQL_DB` consistently
- Fixed `docker-compose.yml` to use `MYSQL_DB`
- Fixed `Makefile` db-init to use `MYSQL_DB`

### **Type Conversion**
- Fixed `common/env_readers.py` to auto-cast env vars to correct types (int, float, bool)
- Now `REQUEST_TIMEOUT_SECONDS=30` is cast to `int(30)` automatically

---

## 📦 **Files Summary**

### **New Files (13)**
1. `agentic/schemas.py`
2. `agentic/quality.py`
3. `pipelines/agentic_controller.py`
4. `configs/agentic.yaml`
5. `db/migrations/2025_10_14_agentic_plan_and_iter.sql`
6. `scripts/run_agentic.py`
7. `scripts/view_agentic_iters.py`
8. `run_agentic.bat`
9. `scripts/run_agentic.sh`
10. `examples/agentic_plan_example.json`
11. `AGENTIC_QUICKSTART.md`
12. `AGENTIC_CHEATSHEET.md`
13. `TEST_AGENTIC.md`

Plus tests:
14. `tests/test_agentic_plan.py`
15. `tests/test_agentic_quality.py`

### **Modified Files (8)**
1. `agentic/llm.py`
2. `db/dao.py`
3. `apps/api/main.py`
4. `common/settings.py`
5. `Makefile`
6. `docker-compose.yml`
7. `README.md`
8. Plus documentation files (QUICK_REFERENCE, START_HERE, etc.)

---

## 🎯 **Impact**

### **Before**
- Linear search: Query → Results → Cache
- Manual query crafting
- No quality filtering beyond basic scoring
- No iteration or refinement
- No audit trail

### **After**
- ✅ Autonomous agentic loop
- ✅ LLM-generated search strategy
- ✅ Multi-layered quality gates
- ✅ Iterative refinement with new queries
- ✅ Full regulatory-compliant audit
- ✅ CLI + API + VSCode debug support
- ✅ Stop conditions (budget, goals, progress)

---

## 📊 **Metrics**

- **Lines of Code:** ~1,800+ new
- **Tests:** 16+ new test cases
- **API Endpoints:** 3 new
- **Database Tables:** 2 new (audit)
- **CLI Commands:** 3 new (run, view, dry-run)
- **VSCode Configs:** 12 debug configurations
- **Documentation Pages:** 4 new guides

---

## 🏆 **Breaking Changes**

### **None! Fully Backward Compatible**

- Old `search_pipeline.py` still works
- Old `ingest_pipeline.py` unchanged (except improvements)
- New agentic system is additive

### **Required Actions**

1. **Update `.env`:**
   ```bash
   # Change from (if you had this):
   MYSQL_DATABASE=reg_cache
   
   # To:
   MYSQL_DB=reg_cache
   ```

2. **Run migrations:**
   ```bash
   make migrate-agentic
   ```

3. **Install if needed:**
   ```bash
   pip install -r requirements.txt
   # (adds trafilatura, beautifulsoup4, lxml - already in requirements.txt)
   ```

---

## 🚀 **Upgrade Path**

### **From v1.x to v2.0:**

```bash
# 1. Pull changes
git pull origin main

# 2. Update .env (MYSQL_DATABASE → MYSQL_DB if needed)
nano .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
make migrate
make migrate-agentic

# 5. Test
python scripts/run_agentic.py --prompt "Test" --dry-run

# 6. Go live!
make agentic-example
```

---

## 📖 **Documentation**

- **[AGENTIC_QUICKSTART.md](AGENTIC_QUICKSTART.md)** - Complete tutorial
- **[AGENTIC_CHEATSHEET.md](AGENTIC_CHEATSHEET.md)** - Quick reference
- **[TEST_AGENTIC.md](TEST_AGENTIC.md)** - Testing & debugging guide
- **[README.md](README.md)** - Updated with full Agentic section
- **[examples/agentic_plan_example.json](examples/agentic_plan_example.json)** - Ready-to-use plan

---

## 🙏 **Credits**

This release transforms the project from a simple search pipeline into a **production-grade agentic system** suitable for regulatory compliance in healthcare.

**Key Innovations:**
- Multi-agent architecture (Planner + Judge + Controller)
- Quality gates with semantic + hard filters
- Full audit trail for regulatory compliance
- Cost control with budgets and stop conditions
- Human-in-the-loop capability (editable plans)

---

## 📅 **Next Steps (Future)**

- [ ] `/agentic/dry-run` endpoint (simulate without DB)
- [ ] Simple web UI for plan visualization
- [ ] Auto-enqueue approved docs for ingestion
- [ ] Backfill anchor_signals for legacy records
- [ ] Prometheus metrics for monitoring
- [ ] Multi-agent orchestration (parallel judges)

---

**Version 2.0.0 - From Linear Search to Autonomous AI! 🤖🚀**

