# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""
EXEMPLO: Como usar GPT-4 Vision para gerar captions de figuras.

Esta é uma proposta de implementação que usa GPT-4 Vision para
analisar imagens/páginas de PDF e gerar captions contextuais.
"""

import base64
import json
import os
from io import BytesIO
from pathlib import Path
from typing import List, Optional

import structlog
from pdf2image import convert_from_path
from PIL import Image

from apps.api.schemas.vision_enrichment import (
    BBox,
    FigureInfo,
    PageOCR,
)

logger = structlog.get_logger()


class GeminiClientWithGPTVision:
    """
    Gemini client que usa GPT-4 Vision para análise de figuras.
    """
    
    def __init__(self, api_key: Optional[str] = None, llm_client: Optional["LLMClient"] = None):
        """
        Initialize client.
        
        Args:
            api_key: Google API key (opcional, para quando Gemini estiver disponível)
            llm_client: LLMClient para GPT Vision
        """
        self.api_key = api_key
        self.llm_client = llm_client
    
    def describe_figures(
        self,
        file_path: str,
        page_ocr: PageOCR,
    ) -> List[FigureInfo]:
        """
        Analyze figures/images in a document page using GPT-4 Vision.
        
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
        
        # Check if GPT Vision is enabled
        use_gpt_vision = os.getenv("USE_GPT_VISION", "false").lower() == "true"
        
        if not use_gpt_vision or not self.llm_client:
            logger.info("gemini_describe_figures_placeholder", msg="Returning empty (set USE_GPT_VISION=true to enable)")
            return []
        
        logger.info("gemini_describe_start", file=path.name, page=page_ocr.page)
        
        try:
            return self._describe_figures_via_gpt_vision(path, page_ocr)
        
        except Exception as e:
            logger.error("gemini_describe_failed", file=path.name, error=str(e))
            return []
    
    def _describe_figures_via_gpt_vision(
        self,
        path: Path,
        page_ocr: PageOCR,
    ) -> List[FigureInfo]:
        """
        Use GPT-4 Vision to analyze figures in the page.
        
        Args:
            path: Path to PDF file
            page_ocr: OCR result for the page
            
        Returns:
            List of FigureInfo
        """
        try:
            # Convert PDF page to image
            images = convert_from_path(
                str(path),
                first_page=page_ocr.page + 1,  # pdf2image is 1-indexed
                last_page=page_ocr.page + 1,
                dpi=150,  # Lower DPI to save tokens
            )
            
            if not images:
                logger.warning("gemini_vision_no_images", page=page_ocr.page)
                return []
            
            image = images[0]
            
            # Resize if too large (to save tokens)
            max_size = 2000
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Build prompt
            prompt = f"""Analise esta página de documento e identifique todas as figuras, diagramas, gráficos ou imagens.

Para cada figura encontrada, forneça:
1. **caption**: Descrição clara do que a figura mostra (1-2 frases)
2. **labels**: 3-5 tags descritivas (ex: "diagram", "flowchart", "chart", "table", "screenshot")
3. **bbox**: Estimativa aproximada da posição (x, y, width, height) em pixels
4. **confidence**: Quão confiante você está (0.0-1.0)

Se NÃO houver figuras/diagramas relevantes na página, retorne uma lista vazia.

FORMATO DE RESPOSTA (JSON puro):
{{
  "figures": [
    {{
      "caption": "Diagrama mostrando arquitetura de RAG com componentes...",
      "labels": ["architecture", "diagram", "rag", "flowchart"],
      "bbox": {{"x": 100, "y": 200, "width": 400, "height": 300}},
      "confidence": 0.92
    }}
  ]
}}

Responda APENAS com o JSON, sem explicações ou markdown."""
            
            logger.info("gemini_vision_calling_gpt", page=page_ocr.page)
            
            # Call GPT-4 Vision
            from openai import OpenAI
            
            client = OpenAI(api_key=self.llm_client.client.api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o",  # or "gpt-4-vision-preview"
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}",
                                    "detail": "low"  # "low" = cheaper, "high" = more detailed
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            figures_data = result.get("figures", [])
            
            # Convert to FigureInfo
            figures = []
            for fig_data in figures_data:
                bbox_data = fig_data.get("bbox", {})
                
                figure = FigureInfo(
                    caption=fig_data.get("caption", ""),
                    labels=fig_data.get("labels", []),
                    bbox=BBox(
                        x=float(bbox_data.get("x", 0)),
                        y=float(bbox_data.get("y", 0)),
                        width=float(bbox_data.get("width", 100)),
                        height=float(bbox_data.get("height", 100)),
                    ),
                    confidence=float(fig_data.get("confidence", 0.7)),
                )
                figures.append(figure)
            
            logger.info(
                "gemini_vision_success",
                page=page_ocr.page,
                count=len(figures)
            )
            
            return figures
        
        except Exception as e:
            logger.error("gemini_vision_failed", page=page_ocr.page, error=str(e))
            return []


# EXEMPLO DE USO:
# 
# from agentic.llm import LLMClient
# 
# llm = LLMClient(api_key="sk-...", model="gpt-4o")
# gemini = GeminiClientWithGPTVision(llm_client=llm)
# 
# figures = gemini.describe_figures(file_path, page_ocr)
# 
# for fig in figures:
#     print(f"Caption: {fig.caption}")
#     print(f"Labels: {fig.labels}")
#     print(f"Confidence: {fig.confidence}")


# CUSTOS ESTIMADOS (GPT-4 Vision):
# 
# Model: gpt-4o
# Input: $2.50 / 1M tokens
# Image (low detail): ~85 tokens por imagem
# 
# Exemplo:
#   10 documentos × 10 páginas = 100 páginas
#   100 × 85 tokens = 8,500 tokens
#   8,500 × $2.50 / 1M = $0.02 (2 centavos!)
# 
# Model: gpt-4-vision-preview
# Input: $10.00 / 1M tokens
# Image (low detail): ~85 tokens por imagem
# 
# Exemplo:
#   10 documentos × 10 páginas = 100 páginas
#   100 × 85 tokens = 8,500 tokens
#   8,500 × $10.00 / 1M = $0.085 (8.5 centavos!)
# 
# NOTA: "low detail" = 85 tokens, "high detail" = 170-765 tokens dependendo do tamanho

