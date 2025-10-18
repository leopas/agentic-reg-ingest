# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Gemini API client wrapper for multimodal interpretation."""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import structlog

from apps.api.schemas.vision_enrichment import (
    BBox,
    EvidenceSpan,
    FigureInfo,
    GuidedInference,
    PageOCR,
)

if TYPE_CHECKING:
    from agentic.llm import LLMClient

logger = structlog.get_logger()


class GeminiClient:
    """Wrapper for Gemini multimodal API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro", llm_client: Optional["LLMClient"] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key (if None, uses GOOGLE_API_KEY env var)
            model: Gemini model name
            llm_client: LLMClient for GPT-based hypothesis generation (optional)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        self.model = model
        self.llm_client = llm_client
        
        if not self.api_key:
            logger.warning("gemini_client_no_api_key", msg="Gemini API key not configured")
    
    def describe_figures(
        self,
        file_path: str,
        page_ocr: PageOCR,
    ) -> List[FigureInfo]:
        """
        Analyze figures/images in a document page.
        
        Args:
            file_path: Path to document file
            page_ocr: OCR result for the page
            
        Returns:
            List of FigureInfo with captions, labels, and bounding boxes
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error("gemini_describe_file_not_found", path=str(path))
            return []
        
        logger.info("gemini_describe_start", file=path.name, page=page_ocr.page)
        
        try:
            # TODO: Implement actual Gemini API call when credentials exist
            # For now, return placeholder
            
            # Placeholder: simulate figure detection
            return self._describe_figures_placeholder(path, page_ocr)
        
        except Exception as e:
            logger.error("gemini_describe_failed", file=path.name, error=str(e))
            return []
    
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
        
        logger.info("gemini_inference_start", file=path.name, page=page_ocr.page)
        
        try:
            # Check if GPT hypothesis generation is enabled
            use_gpt_hypothesis = os.getenv("USE_GPT_HYPOTHESIS", "false").lower() == "true"
            
            # If LLM client available and enabled, use GPT for hypothesis
            if use_gpt_hypothesis and self.llm_client:
                # Check if text is sufficient
                if page_ocr.text and len(page_ocr.text.strip()) >= 50:
                    return self._generate_inferences_via_gpt(page_ocr, context_window)
                else:
                    logger.warning("gemini_inference_insufficient_text", page=page_ocr.page)
                    return []
            
            # Fallback: return empty (avoid confusing GPT allowlist planner)
            logger.info("gemini_inference_placeholder", file=path.name, msg="Returning empty (set USE_GPT_HYPOTHESIS=true to enable)")
            return []
        
        except Exception as e:
            logger.error("gemini_inference_failed", file=path.name, error=str(e))
            return []
    
    def _describe_figures_placeholder(self, path: Path, page_ocr: PageOCR) -> List[FigureInfo]:
        """Placeholder figure description."""
        logger.info("gemini_figures_placeholder", file=path.name, msg="Skipping figures (placeholder mode)")
        
        # ✅ Return empty list to avoid confusing GPT with hardcoded captions
        # Real Gemini API will generate actual figure descriptions based on image content
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
        
        # Limit text size to avoid token limits
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
            logger.info("gemini_inference_calling_gpt", page=page_ocr.page)
            
            # Call GPT
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
            
            # Parse response
            result = json.loads(response)
            inferences_data = result.get("inferences", [])
            
            # Convert to GuidedInference
            inferences = []
            for inf_data in inferences_data[:3]:  # Max 3
                # Find evidence spans (first 200 chars as example)
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
            logger.error("gemini_inference_gpt_failed", page=page_ocr.page, error=str(e))
            return []

