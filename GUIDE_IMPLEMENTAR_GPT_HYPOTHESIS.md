# 🔧 Guia: Implementar GPT Hypothesis

## Estratégia Recomendada: GPT-4o-mini

### Passo 1: Modificar `pipelines/enrichment_pipeline.py`

```python
# Linha ~47: Inicializar LLMClient se não existir
if not self.gemini_client:
    # Passar llm_client para GeminiClient
    from agentic.llm import LLMClient
    
    llm = LLMClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=0.0
    )
    
    self.gemini_client = GeminiClient(llm_client=llm)
```

### Passo 2: Modificar `agentic/vision/gemini_client.py`

```python
# Adicionar __init__ com llm_client opcional
def __init__(self, api_key: Optional[str] = None, llm_client: Optional["LLMClient"] = None):
    self.api_key = api_key
    self.llm_client = llm_client  # ← NOVO!
```

### Passo 3: Modificar `guided_inferences()`

```python
def guided_inferences(self, file_path: str, page_ocr: PageOCR, ...) -> List[GuidedInference]:
    # ...
    
    # ✅ Se tiver LLM client, usa GPT
    if self.llm_client:
        return self._generate_inferences_via_gpt(page_ocr)
    else:
        # Fallback: retorna vazio
        return []
```

### Passo 4: Adicionar `_generate_inferences_via_gpt()`

**Copie o método do arquivo:**
`agentic/vision/gemini_client_gpt_hypothesis.py`

```python
def _generate_inferences_via_gpt(self, page_ocr: PageOCR, ...) -> List[GuidedInference]:
    text = page_ocr.text
    text_preview = text[:1500]  # Limita para não estourar prompt
    
    prompt = f"""Analise o texto e identifique 1-3 hipóteses principais...
    
    TEXTO: {text_preview}
    
    FORMATO: {{"inferences": [...]}}
    """
    
    response = self.llm_client._call_chat_completion(...)
    result = json.loads(response)
    
    # Converte para GuidedInference
    inferences = []
    for inf_data in result["inferences"]:
        inference = GuidedInference(
            hypothesis=inf_data["hypothesis"],
            rationale=inf_data["rationale"],
            confidence=inf_data["confidence"],
            ...
        )
        inferences.append(inference)
    
    return inferences
```

### Passo 5: Ativar com Variável de Ambiente

```bash
# .env
USE_GPT_HYPOTHESIS=true
```

### Passo 6: Testar!

```bash
# Fazer novo upload
# Verificar JSONL gerado
cat data/output/jsonl/xxx.jsonl | jq '.guided_inferences'

# Deve mostrar hipóteses REAIS, não vazias!
```

---

## Custos Estimados

| Documento | Páginas | Tokens | Custo (GPT-4o-mini) |
|-----------|---------|--------|---------------------|
| Pequeno   | 5       | ~2k    | $0.0003            |
| Médio     | 20      | ~8k    | $0.0012            |
| Grande    | 100     | ~40k   | $0.0060            |

**Menos de 1 centavo por documento!**

---

## Alternativa: Usar Apenas Heurística

Se custo for crítico, use heurística:

```python
def _generate_inferences_heuristic(self, page_ocr: PageOCR) -> List[GuidedInference]:
    text = page_ocr.text.lower()
    
    hypotheses = []
    
    # Detectar domínio
    if "rag" in text and ("production" in text or "llm" in text):
        hypotheses.append({
            "hypothesis": "Documento técnico sobre RAG e sistemas de produção",
            "confidence": 0.75
        })
    
    if "ans" in text or "anvisa" in text:
        hypotheses.append({
            "hypothesis": "Documento sobre regulamentação em saúde",
            "confidence": 0.80
        })
    
    # Converter para GuidedInference
    inferences = []
    for h in hypotheses:
        inference = GuidedInference(
            hypothesis=h["hypothesis"],
            rationale="Detectado por análise de keywords",
            confidence=h["confidence"],
            evidence_spans=[...],
            section_hint="Inferido"
        )
        inferences.append(inference)
    
    return inferences
```

---

## Conclusão

**RECOMENDAÇÃO:** Use GPT-4o-mini!

✅ Preciso
✅ Barato (~$0.0001/página)
✅ Manutenção zero
✅ Funciona para qualquer domínio

**Custos são INSIGNIFICANTES comparados ao valor da precisão!**

