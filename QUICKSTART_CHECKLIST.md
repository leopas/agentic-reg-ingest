# ✅ Checklist de Setup Rápido

Use este checklist para garantir que tudo está configurado antes de rodar o debug.

## 📋 Passo a Passo

### ☐ 1. Virtual Environment

```bash
# Criar .venv (se ainda não existe)
python3.11 -m venv .venv

# Windows PowerShell
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Confirmar que está ativo (deve mostrar (.venv) no prompt)
```

**✅ Checkpoint**: O prompt deve mostrar `(.venv)` no início

---

### ☐ 2. Instalar Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

**✅ Checkpoint**: Rodar `pip list` deve mostrar fastapi, sqlalchemy, openai, etc.

---

### ☐ 3. Configurar .env

```bash
# Copiar exemplo
cp .env.example .env

# Editar .env com suas credenciais
code .env  # ou use seu editor favorito
```

**Variáveis OBRIGATÓRIAS para Search Pipeline**:
```env
GOOGLE_API_KEY=sua-chave-aqui       # ← Obtenha em: https://console.cloud.google.com/
GOOGLE_CX=seu-cx-aqui                # ← Custom Search Engine ID
OPENAI_API_KEY=sk-xxx                # ← API key da OpenAI
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=reg_cache
MYSQL_USER=root
MYSQL_PASSWORD=sua-senha-mysql
```

**✅ Checkpoint**: Arquivo `.env` existe e tem todas as variáveis preenchidas

---

### ☐ 4. MySQL via Docker

```bash
# Iniciar MySQL
docker compose up -d mysql

# Verificar status
docker compose ps

# Aguardar ~10 segundos para MySQL inicializar
```

**✅ Checkpoint**: `docker compose ps` mostra mysql como "Up" e "healthy"

---

### ☐ 5. Inicializar Banco de Dados

```bash
# Opção 1: Via Makefile
make db-init

# Opção 2: Via Python
python -c "from db.session import init_db; from common.env_readers import load_yaml_with_env; init_db(load_yaml_with_env('configs/db.yaml'))"

# Opção 3: Via MySQL CLI
docker compose exec mysql mysql -u root -p${MYSQL_PASSWORD} reg_cache < db/schema.sql
```

**✅ Checkpoint**: Não deve ter erros. Tabelas criadas com sucesso.

**Verificar tabelas**:
```bash
docker compose exec mysql mysql -u root -p${MYSQL_PASSWORD} reg_cache -e "SHOW TABLES;"
```

Deve mostrar:
```
+----------------------+
| Tables_in_reg_cache  |
+----------------------+
| document_catalog     |
| search_query         |
| search_result        |
+----------------------+
```

---

### ☐ 6. Selecionar Interpretador Python no VSCode

1. Pressione `Ctrl+Shift+P` (ou `Cmd+Shift+P` no Mac)
2. Digite: `Python: Select Interpreter`
3. Escolha: `.venv/bin/python` ou `.venv\Scripts\python.exe`

**✅ Checkpoint**: Barra de status inferior mostra `.venv` como interpretador

---

### ☐ 7. Testar Credenciais (Opcional mas Recomendado)

```bash
# Testar Google CSE
python -c "
from common.settings import settings
print(f'Google API Key: {settings.google_api_key[:10]}...')
print(f'Google CX: {settings.google_cx}')
"

# Testar OpenAI
python -c "
from common.settings import settings
print(f'OpenAI Key: {settings.openai_api_key[:10]}...')
"
```

**✅ Checkpoint**: Deve imprimir os primeiros caracteres das chaves (não "your-key-here")

---

## 🎯 Pronto para Debugar!

Se todos os checkpoints acima passaram, você está pronto! 

### Iniciar Debug da Search Pipeline:

1. Abra `pipelines/search_pipeline.py`
2. Coloque um breakpoint na linha ~87 (função `execute`)
3. Pressione `F5`
4. Selecione **"Debug: Search Pipeline"**
5. Observe a execução pausar no breakpoint!

---

## 🚨 Troubleshooting Rápido

### Erro: "ModuleNotFoundError"
```bash
# Reinstalar dependências
pip install -r requirements.txt

# Verificar PYTHONPATH
export PYTHONPATH=$PWD  # Linux/Mac
$env:PYTHONPATH = $PWD  # Windows PowerShell
```

### Erro: "Can't connect to database"
```bash
# Reiniciar MySQL
docker compose restart mysql

# Aguardar 10 segundos
sleep 10

# Testar conexão
docker compose exec mysql mysql -u root -p -e "SELECT 1;"
```

### Erro: "Invalid API key"
```bash
# Verificar se .env está sendo lido
python -c "from common.settings import settings; print(settings.google_api_key)"

# Se aparecer "your-google-api-key-here", o .env não está configurado
```

### MySQL não inicia
```bash
# Ver logs
docker compose logs mysql

# Remover volume e reiniciar (⚠️ apaga dados)
docker compose down -v
docker compose up -d mysql
```

---

## 📞 Precisa de Ajuda?

Abra uma issue no GitHub ou consulte:
- `README.md` - Documentação completa
- `DEBUG_GUIDE.md` - Guia detalhado de debug
- `CONTRIBUTING.md` - Guidelines de contribuição

**Boa sorte! 🚀**

