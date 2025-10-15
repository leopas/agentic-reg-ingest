# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Embedding encoder with configurable provider."""

import os
import structlog
from typing import List

import numpy as np

logger = structlog.get_logger()

# Environment configuration
PROVIDER = os.getenv("EMBED_PROVIDER", "openai").lower()
MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))


def encode_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for texts using configured provider.
    
    Supports:
    - OpenAI (default)
    - Azure OpenAI
    - Local LLM (LM Studio/Ollama via OpenAI-compatible API)
    - Fallback dummy (for testing only)
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors (one per text)
    """
    if not texts:
        return []
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    
    logger.info("encode_start", provider=PROVIDER, model=MODEL, texts=len(texts), has_api_key=bool(api_key))
    
    # Try OpenAI/compatible if API key exists
    if api_key:
        try:
            from openai import OpenAI
            
            base_url = os.getenv("OPENAI_BASE_URL")
            
            logger.info("encode_openai_init", base_url=base_url or "default")
            
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,  # None for OpenAI default
            )
            
            # OpenAI API supports batching
            logger.info("encode_calling_api", model=MODEL, texts=len(texts))
            
            response = client.embeddings.create(
                model=MODEL,
                input=texts,
            )
            
            embeddings = [item.embedding for item in response.data]
            
            actual_dim = len(embeddings[0]) if embeddings else 0
            
            logger.info("encode_done", embeddings=len(embeddings), dim=actual_dim, model=MODEL)
            
            return embeddings
        
        except Exception as e:
            logger.error("encode_failed", provider=PROVIDER, error=str(e), error_type=type(e).__name__)
            raise
    
    # Fallback: dummy embeddings (DO NOT USE IN PRODUCTION)
    logger.warning(
        "encode_dummy_fallback",
        provider=PROVIDER,
        dim=EMBED_DIM,
        reason="NO OPENAI_API_KEY - using random vectors!",
        msg="⚠️ DUMMY EMBEDDINGS - NOT FOR PRODUCTION!"
    )
    
    rng = np.random.default_rng(42)
    embeddings = [rng.normal(size=EMBED_DIM).astype(float).tolist() for _ in texts]
    
    return embeddings


def get_embedding_dim() -> int:
    """
    Get embedding dimension for current configuration.
    
    Returns:
        Embedding dimension
    """
    return EMBED_DIM

