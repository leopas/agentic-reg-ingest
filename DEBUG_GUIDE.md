# Guia de Debug no VSCode/Cursor

## 🚀 Como Debugar a Search Pipeline

### Passo 1: Configurar o .env

Antes de debugar, certifique-se de que o arquivo `.env` existe e está configurado:

```bash
# Se ainda não existe, copie o exemplo
cp .env.example .env
```

Edite o `.env` e configure:
```env
GOOGLE_API_KEY=sua-chave-google-aqui
GOOGLE_CX=seu-custom-search-id-aqui
OPENAI_API_KEY=sk-sua-chave-openai
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=reg_cache
MYSQL_USER=root
MYSQL_PASSWORD=sua-senha
```

### Passo 2: Garantir que o MySQL está rodando

```bash
# Via Docker
docker compose up -d mysql

# Verificar se está rodando
docker compose ps
```

### Passo 3: Inicializar o banco (primeira vez)

```bash
# No terminal do VSCode (Ctrl+`)
make db-init

# OU manualmente
python -c "from db.session import init_db; from common.env_readers import load_yaml_with_env; init_db(load_yaml_with_env('configs/db.yaml'))"
```

### Passo 4: Debugar a Search Pipeline

1. **Abra o arquivo** `pipelines/search_pipeline.py`

2. **Coloque breakpoints** clicando à esquerda do número da linha (aparece um círculo vermelho)
   - Sugestões de breakpoints:
     - Linha ~87: `def execute()`
     - Linha ~100: após carregar cache
     - Linha ~115: após executar CSE
     - Linha ~135: após calcular score

3. **Abra o painel de Debug**:
   - Pressione `Ctrl+Shift+D` (Windows/Linux)
   - Ou `Cmd+Shift+D` (Mac)
   - Ou clique no ícone de "play com bug" na barra lateral

4. **Selecione a configuração**: 
   - No dropdown do topo, escolha **"Debug: Search Pipeline"**

5. **Inicie o debug**:
   - Pressione `F5` ou clique no botão verde "▶ Start Debugging"

6. **Controles do Debug**:
   - `F5` - Continue (continuar até próximo breakpoint)
   - `F10` - Step Over (executar linha atual)
   - `F11` - Step Into (entrar na função)
   - `Shift+F11` - Step Out (sair da função)
   - `Ctrl+Shift+F5` - Restart
   - `Shift+F5` - Stop

### Passo 5: Inspecionar Variáveis

Durante o debug, você pode:

- **Ver variáveis locais**: Painel "Variables" à esquerda
- **Avaliar expressões**: Painel "Watch" - adicione expressões para monitorar
- **Console interativo**: Painel "Debug Console" - execute comandos Python
- **Call Stack**: Ver a pilha de chamadas

## 🔍 Exemplo de Debug Session

```python
# Ao pausar no breakpoint dentro de execute():

# No Debug Console, você pode:
>>> cache_key
'a3f5b8c9d1e2...'

>>> len(items)
10

>>> items[0]['title']
'Resolução Normativa 259'

>>> self.scorer.score(...)
3.456
```

## 📝 Dicas Úteis

### Mudar a Query de Busca

Edite em `.vscode/launch.json`:
```json
"args": [
    "--query", "TISS ANS",  // <-- Mude aqui
    "--topn", "20"          // <-- Ou limite de resultados
]
```

### Debug com menos resultados

Para testar mais rápido, reduza o `--topn`:
```json
"args": [
    "--query", "RN 259 ANS",
    "--topn", "5"  // <-- Apenas 5 resultados
]
```

### Debug Condicional

Clique com botão direito no breakpoint → "Edit Breakpoint" → "Conditional":
```python
# Parar apenas quando score > 3.0
score > 3.0

# Parar apenas para domínios .gov.br
'.gov.br' in url

# Parar na 10ª iteração
idx == 9
```

### Logpoints

Em vez de breakpoint, adicione um "Logpoint" (não para a execução):
- Botão direito → "Add Logpoint"
- Digite: `Score: {score}, URL: {url}`

## 🐛 Outras Configurações de Debug

### Debug: Ingest Pipeline
```
Executa a pipeline de ingestão
Útil para debugar processamento de PDFs/ZIPs/HTML
```

### Debug: FastAPI Server
```
Inicia servidor FastAPI em modo debug
Breakpoints funcionam ao fazer requisições HTTP
```

### Debug: Current Python File
```
Debuga o arquivo Python atualmente aberto
Útil para testar módulos individuais
```

### Debug: Pytest
```
Debuga testes unitários
Escolha "Debug: Pytest Current File" ou "Debug: All Tests"
```

## 🆘 Troubleshooting

### Erro: "No module named 'agentic'"
- Certifique-se de que está usando o interpretador do `.venv`
- Pressione `Ctrl+Shift+P` → "Python: Select Interpreter" → escolha `.venv/bin/python`

### Erro: "Missing GOOGLE_API_KEY"
- Verifique se o arquivo `.env` existe
- Verifique se as variáveis estão definidas corretamente

### Erro: "Can't connect to MySQL"
- Verifique se o MySQL está rodando: `docker compose ps`
- Verifique as credenciais em `.env`
- Teste conexão: `mysql -h localhost -u root -p`

### Debug muito lento
- Use `--topn 5` para menos resultados
- Desabilite "justMyCode": false para debugar bibliotecas externas
- Use Logpoints em vez de Breakpoints onde possível

## 📊 Monitorando a Execução

### Ver logs estruturados
Os logs JSON aparecem no terminal integrado. Para melhor visualização:

```bash
# Instalar jq (JSON processor)
# Windows (via chocolatey)
choco install jq

# Linux
sudo apt install jq

# Mac
brew install jq

# Então você pode filtrar logs:
python pipelines/search_pipeline.py ... | jq .
```

### Verificar o banco de dados

```bash
# Conectar ao MySQL
docker compose exec mysql mysql -u root -p reg_cache

# Ver queries em cache
SELECT * FROM search_query ORDER BY created_at DESC LIMIT 5;

# Ver resultados
SELECT url, title, score FROM search_result ORDER BY score DESC LIMIT 10;
```

---

**Pronto para debugar! 🚀**

Pressione `F5` e comece a explorar o código em tempo real!

