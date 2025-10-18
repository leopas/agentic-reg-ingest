# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Google Vision API client wrapper for OCR."""

import io
import os
from pathlib import Path
from typing import List, Optional

import structlog
from google.cloud import vision
from pdf2image import convert_from_path
from PIL import Image

from apps.api.schemas.vision_enrichment import PageOCR

logger = structlog.get_logger()


class VisionClient:
    """Wrapper for Google Vision API OCR."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Vision client.
        
        Args:
            api_key: Google API key (if None, uses GOOGLE_API_KEY env var or GOOGLE_APPLICATION_CREDENTIALS)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        
        # Initialize Vision client
        try:
            if self.api_key:
                # Use API key authentication
                os.environ["GOOGLE_API_KEY"] = self.api_key
            
            self.vision_client = vision.ImageAnnotatorClient()
            logger.info("vision_client_initialized", auth_method="api_key" if self.api_key else "credentials")
        
        except Exception as e:
            logger.warning("vision_client_init_failed", error=str(e), msg="Will fallback to pdfplumber")
            self.vision_client = None
    
    def extract_text(self, file_path: str) -> List[PageOCR]:
        """
        Extract text from document using OCR.
        
        Args:
            file_path: Path to document file (.pdf, .pptx, etc.)
            
        Returns:
            List of PageOCR objects with extracted text per page
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error("vision_extract_file_not_found", path=str(path))
            return []
        
        logger.info("vision_extract_start", file=path.name)
        
        try:
            # TODO: Implement actual Google Vision API call when credentials exist
            # For now, return placeholder
            
            # Placeholder: simulate OCR for different file types
            if path.suffix.lower() == ".pdf":
                return self._extract_pdf_placeholder(path)
            elif path.suffix.lower() in [".pptx", ".ppt"]:
                return self._extract_pptx_placeholder(path)
            else:
                logger.warning("vision_unsupported_format", suffix=path.suffix)
                return []
        
        except Exception as e:
            logger.error("vision_extract_failed", file=path.name, error=str(e))
            return []
    
    def _extract_pdf_placeholder(self, path: Path) -> List[PageOCR]:
        """Extract text from PDF using Google Vision API OCR."""
        
        # Configuração: Use Vision API ou fallback
        use_vision_api = os.getenv("USE_VISION_API", "false").lower() == "true"
        
        logger.info(
            "vision_decision_point",
            use_vision_api=use_vision_api,
            client_available=self.vision_client is not None,
            file=path.name
        )
        
        if not use_vision_api or not self.vision_client:
            logger.info("vision_using_fallback", msg="Using pdfplumber (set USE_VISION_API=true for Vision API)")
            return self._extract_pdf_fallback(path)
        
        try:
            logger.info("vision_pdf_extract_start", file=path.name, method="google_vision_api")
            
            # Convert PDF to images (one per page)
            logger.info("vision_pdf_converting", file=path.name, msg="Converting PDF to images...")
            images = convert_from_path(str(path), dpi=300, fmt='png')
            
            logger.info("vision_pdf_pages", file=path.name, total_pages=len(images))
            
            pages_ocr = []
            
            for page_num, image in enumerate(images, start=1):
                try:
                    # Convert PIL Image to bytes
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    # Call Vision API
                    logger.debug("vision_api_calling", page=page_num)
                    
                    image_obj = vision.Image(content=img_bytes)
                    response = self.vision_client.document_text_detection(image=image_obj)
                    
                    if response.error.message:
                        logger.error("vision_api_error", page=page_num, error=response.error.message)
                        pages_ocr.append(PageOCR(
                            page=page_num,
                            text=f"[Erro no OCR da página {page_num}]",
                            confidence=0.0
                        ))
                        continue
                    
                    # Extract text
                    text = response.full_text_annotation.text if response.full_text_annotation else ""
                    
                    # Calculate average confidence
                    confidence = self._calculate_confidence(response)
                    
                    pages_ocr.append(PageOCR(
                        page=page_num,
                        text=text.strip() if text else "[Página vazia]",
                        confidence=confidence
                    ))
                    
                    logger.debug("vision_page_extracted", page=page_num, chars=len(text), confidence=confidence)
                
                except Exception as e:
                    logger.error("vision_page_failed", page=page_num, error=str(e))
                    pages_ocr.append(PageOCR(
                        page=page_num,
                        text=f"[Erro ao processar página {page_num}: {str(e)}]",
                        confidence=0.0
                    ))
            
            logger.info(
                "vision_pdf_extract_done",
                file=path.name,
                method="google_vision_api",
                pages_extracted=len(pages_ocr),
                total_chars=sum(len(p.text) for p in pages_ocr),
                avg_confidence=sum(p.confidence for p in pages_ocr) / len(pages_ocr) if pages_ocr else 0
            )
            
            return pages_ocr
        
        except Exception as e:
            logger.error("vision_pdf_extract_failed", file=path.name, error=str(e), msg="Falling back to pdfplumber")
            return self._extract_pdf_fallback(path)
    
    def _extract_pdf_fallback(self, path: Path) -> List[PageOCR]:
        """Fallback: Extract text from PDF using pdfplumber."""
        try:
            import pdfplumber
            
            logger.info("vision_pdf_fallback", file=path.name, method="pdfplumber")
            
            pages_ocr = []
            
            with pdfplumber.open(path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    
                    if text and len(text.strip()) > 0:
                        pages_ocr.append(PageOCR(
                            page=page_num,
                            text=text.strip(),
                            confidence=1.0
                        ))
                    else:
                        pages_ocr.append(PageOCR(
                            page=page_num,
                            text="[Página vazia]",
                            confidence=0.0
                        ))
            
            return pages_ocr
        
        except Exception as e:
            logger.error("vision_fallback_failed", file=path.name, error=str(e))
            return [PageOCR(page=1, text="[Erro ao extrair texto]", confidence=0.0)]
    
    def _calculate_confidence(self, response) -> float:
        """Calculate average confidence from Vision API response."""
        try:
            if not response.full_text_annotation:
                return 0.0
            
            # Get confidence from all text blocks
            confidences = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    if hasattr(block, 'confidence'):
                        confidences.append(block.confidence)
            
            return sum(confidences) / len(confidences) if confidences else 0.9
        
        except Exception:
            return 0.9  # Default confidence
    
    def _extract_pptx_placeholder(self, path: Path) -> List[PageOCR]:
        """Placeholder OCR extraction for PPTX."""
        logger.info("vision_pptx_placeholder", file=path.name)
        
        # Return simulated result
        return [
            PageOCR(
                page=1,
                text="[OCR Placeholder] Slide 1: Título do documento. Conteúdo extraído via Vision API.",
                confidence=0.92,
            )
        ]

