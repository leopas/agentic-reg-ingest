<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# 🚀 COMEÇAR AQUI - Guia Rápido de Execução

## ✅ Status Atual
- ✅ Virtual environment criado
- ✅ Dependências instaladas
- ✅ Arquivo .env existe

## 📝 PASSO A PASSO PARA RODAR AGORA

### PASSO 1: Configurar .env com suas credenciais
```powershell
# Abrir .env no VSCode
code .env
```

**Você PRECISA configurar estas variáveis:**
```env
GOOGLE_API_KEY=sua-chave-google-aqui       # Obtenha em: https://console.cloud.google.com/
GOOGLE_CX=seu-custom-search-id             # Configure em: https://programmablesearchengine.google.com/
OPENAI_API_KEY=sk-sua-chave-openai         # Obtenha em: https://platform.openai.com/api-keys

# Para o MySQL local, pode manter assim:
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=reg_cache
MYSQL_USER=root
MYSQL_PASSWORD=root
```

### PASSO 2: Subir MySQL via Docker
```powershell
# Iniciar MySQL
docker compose up -d mysql

# Verificar status (aguarde ficar "healthy")
docker compose ps

# Ver logs se necessário
docker compose logs -f mysql
```

**Aguarde ~15 segundos** para o MySQL inicializar completamente.

### PASSO 3: Criar tabelas no banco
```powershell
# Opção fácil
python -c "from db.session import init_db; from common.env_readers import load_yaml_with_env; init_db(load_yaml_with_env('configs/db.yaml'))"

# OU via Makefile (se funcionar no Windows)
make db-init
```

### PASSO 4: Rodar a Search Pipeline!

**Opção A: Via Python diretamente**
```powershell
python pipelines/search_pipeline.py --config configs/cse.yaml --db configs/db.yaml --query "RN 259 ANS" --topn 10
```

**Opção B: Via Debug no VSCode/Cursor** (RECOMENDADO)
1. Abra `pipelines/search_pipeline.py`
2. Coloque um breakpoint na linha ~87 (função `execute`)
3. Pressione `F5`
4. Selecione: **"Debug: Search Pipeline"**
5. Observe a execução!

**Opção C: Via Makefile**
```powershell
make search
```

## 🎯 Testando sem Google API (se não tiver ainda)

Se você ainda não tem as credenciais do Google, pode testar rodando os **testes**:

```powershell
# Rodar testes
pytest tests/test_scoring.py -v

# Ou todos
pytest tests/ -v
```

## 🌐 Testar API FastAPI

```powershell
# Subir servidor
uvicorn apps.api.main:app --reload --port 8000

# OU via debug
# F5 → Selecione "Debug: FastAPI Server"

# Acessar no navegador
# http://localhost:8000
# http://localhost:8000/docs  (Swagger UI)
```

## 🔍 Verificar se tudo está OK

```powershell
# Teste rápido de imports
python -c "from agentic.cse_client import CSEClient; from db.models import SearchQuery; print('✅ Imports OK!')"

# Ver se .env está sendo lido
python -c "from common.settings import settings; print(f'Google API: {settings.google_api_key[:10]}...')"
```

## ❌ Problemas Comuns

### "ModuleNotFoundError"
```powershell
# Certifique-se que o venv está ativo
.venv\Scripts\activate

# Reinstale
pip install -r requirements.txt
```

### "Can't connect to MySQL"
```powershell
# Reiniciar MySQL
docker compose restart mysql

# Aguardar 10 segundos
Start-Sleep -Seconds 10

# Testar conexão
docker compose exec mysql mysql -u root -proot -e "SELECT 1;"
```

### "ValidationError: GOOGLE_API_KEY"
```
Você precisa configurar o .env!
Abra o arquivo e preencha as credenciais.
```

## 🎓 Próximos Passos

Depois que a search pipeline funcionar:

1. **Ingest Pipeline:**
   ```powershell
   python pipelines/ingest_pipeline.py --config configs/ingest.yaml --db configs/db.yaml --limit 5
   ```

2. **Explorar Database:**
   ```powershell
   docker compose exec mysql mysql -u root -proot reg_cache
   # SQL: SELECT * FROM search_query;
   ```

3. **Ler os guias:**
   - `DEBUG_GUIDE.md` - Debug detalhado
   - `QUICK_REFERENCE.md` - Comandos úteis
   - `README.md` - Documentação completa

---

**Você está pronto! 🚀**

Qualquer dúvida, consulte os arquivos de documentação ou abra uma issue.

