# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""
EXEMPLO: Como usar GPT para gerar hypothesis em vez de placeholder.

Esta é uma proposta de implementação que usa o LLMClient (GPT) para
analisar o texto extraído do OCR e gerar hipóteses contextuais.
"""

import json
from pathlib import Path
from typing import List, Optional

import structlog

from agentic.llm import LLMClient
from apps.api.schemas.vision_enrichment import (
    EvidenceSpan,
    GuidedInference,
    PageOCR,
)

logger = structlog.get_logger()


class GeminiClientWithGPTHypothesis:
    """
    Gemini client que usa GPT para gerar hipóteses quando Gemini não está disponível.
    """
    
    def __init__(self, api_key: Optional[str] = None, llm_client: Optional[LLMClient] = None):
        """
        Initialize client.
        
        Args:
            api_key: Google API key (opcional, para quando Gemini estiver disponível)
            llm_client: LLMClient para gerar hipóteses via GPT
        """
        self.api_key = api_key
        self.llm_client = llm_client
    
    def guided_inferences(
        self,
        file_path: str,
        page_ocr: PageOCR,
        context_window: Optional[str] = None,
    ) -> List[GuidedInference]:
        """
        Generate guided inferences from document context.
        
        Args:
            file_path: Path to document file
            page_ocr: OCR result for the page
            context_window: Additional context from surrounding pages
            
        Returns:
            List of GuidedInference with hypotheses and evidence
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error("gemini_inference_file_not_found", path=str(path))
            return []
        
        # Se não tiver texto, retorna vazio
        if not page_ocr.text or len(page_ocr.text.strip()) < 50:
            logger.warning("gemini_inference_insufficient_text", page=page_ocr.page)
            return []
        
        logger.info("gemini_inference_start", file=path.name, page=page_ocr.page)
        
        try:
            # Se tiver LLM client, usa GPT para gerar hipóteses
            if self.llm_client:
                return self._generate_inferences_via_gpt(page_ocr, context_window)
            else:
                # Fallback: retorna vazio
                logger.info("gemini_inference_no_llm", msg="No LLM client, returning empty")
                return []
        
        except Exception as e:
            logger.error("gemini_inference_failed", file=path.name, error=str(e))
            return []
    
    def _generate_inferences_via_gpt(
        self,
        page_ocr: PageOCR,
        context_window: Optional[str] = None,
    ) -> List[GuidedInference]:
        """
        Generate inferences using GPT.
        
        Args:
            page_ocr: OCR result for the page
            context_window: Optional context from surrounding pages
            
        Returns:
            List of GuidedInference
        """
        text = page_ocr.text
        
        # Limita o tamanho do texto (para não estourar prompt)
        text_preview = text[:1500] if len(text) > 1500 else text
        
        prompt = f"""Você é um especialista em análise de documentos técnicos e regulatórios.

TEXTO DA PÁGINA {page_ocr.page + 1}:
{text_preview}

TAREFA:
Analise o texto acima e identifique 1-3 hipóteses principais (insights, temas, conceitos-chave).

Para cada hipótese, forneça:
1. **hypothesis**: Uma afirmação clara sobre o que o texto trata (1 frase)
2. **rationale**: Por que você chegou a essa conclusão (2-3 frases)
3. **confidence**: Quão confiante você está (0.0-1.0)
4. **section_hint**: Seção/capítulo inferido (ex: "Introdução", "Metodologia", etc.)

REGRAS:
- Máximo 3 hipóteses
- Hipóteses devem ser ESPECÍFICAS ao conteúdo (não genéricas)
- Base-se APENAS no texto fornecido
- Se o texto for muito técnico, identifique o domínio (ex: "IA/ML", "Saúde", "Finanças")
- Se for regulatório, identifique órgãos/normas mencionados

FORMATO DE RESPOSTA (JSON puro):
{{
  "inferences": [
    {{
      "hypothesis": "Este documento trata de...",
      "rationale": "Baseado na presença de termos como X, Y, Z e o contexto...",
      "confidence": 0.85,
      "section_hint": "Capítulo 1 - Introdução"
    }}
  ]
}}

Responda APENAS com o JSON, sem explicações ou markdown."""
        
        try:
            # Chama GPT
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert document analyst. Respond only with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.llm_client._call_chat_completion(
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            # Parse resposta
            result = json.loads(response)
            inferences_data = result.get("inferences", [])
            
            # Converte para GuidedInference
            inferences = []
            for inf_data in inferences_data[:3]:  # Máximo 3
                # Encontra spans de evidência (primeiros 200 chars como exemplo)
                evidence_text = text[:min(200, len(text))]
                
                inference = GuidedInference(
                    hypothesis=inf_data.get("hypothesis", "Hipótese não especificada"),
                    rationale=inf_data.get("rationale", ""),
                    evidence_spans=[
                        EvidenceSpan(
                            start=0,
                            end=len(evidence_text),
                            text=evidence_text,
                        )
                    ],
                    confidence=float(inf_data.get("confidence", 0.7)),
                    section_hint=inf_data.get("section_hint", ""),
                )
                inferences.append(inference)
            
            logger.info(
                "gemini_inference_gpt_success",
                page=page_ocr.page,
                count=len(inferences)
            )
            
            return inferences
        
        except Exception as e:
            logger.error("gemini_inference_gpt_failed", error=str(e))
            return []


# EXEMPLO DE USO:
# 
# from agentic.llm import LLMClient
# 
# llm = LLMClient(api_key="sk-...", model="gpt-4o-mini")
# gemini = GeminiClientWithGPTHypothesis(llm_client=llm)
# 
# inferences = gemini.guided_inferences(file_path, page_ocr)
# 
# for inf in inferences:
#     print(f"Hipótese: {inf.hypothesis}")
#     print(f"Confiança: {inf.confidence}")

