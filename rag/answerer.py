# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""RAG answerer with grounded and inference modes."""

import os
import structlog
from textwrap import dedent
from typing import Any, Dict, List, Optional

from openai import OpenAI

logger = structlog.get_logger()

SYSTEM_BASE = """Você é um assistente especializado em regulatório da saúde suplementar (ANS/TISS).
Responda de forma clara, profissional e direta. Sempre informe uma seção "Fontes consideradas" com título(s) e URL(s).
Se estiver no modo GROUNDED, NUNCA invente informações além dos trechos fornecidos.
Se estiver no modo INFERENCE, você pode inferir com base nos trechos, mas deixe claro que é inferência."""


def _get_client() -> OpenAI:
    """Get OpenAI client."""
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Format chunks into context string for LLM.
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        Formatted context string
    """
    out = []
    
    for idx, chunk in enumerate(chunks):
        title = chunk.get("title") or chunk.get("url") or "Documento"
        score = chunk.get("score", 0.0)
        url = chunk.get("url", "")
        text = chunk.get("text", "").strip().replace("\n", " ")
        
        # Truncate long texts
        if len(text) > 1200:
            text = text[:1200] + "..."
        
        header = f"[Trecho {idx + 1}] {title} (relevância={score:.3f})"
        source = f"URL: {url}" if url else ""
        
        out.append(f"{header}\n{source}\n---\n{text}\n")
    
    return "\n\n".join(out)


def grounded_answer(question: str, chunks: List[Dict[str, Any]], temperature: float = 0.0) -> str:
    """
    Generate grounded answer (only based on retrieved chunks).
    
    Args:
        question: User question
        chunks: Retrieved chunks
        temperature: LLM temperature (0 for deterministic)
        
    Returns:
        Answer text
    """
    logger.info("rag_grounded_start", question=question[:100], chunks=len(chunks))
    
    ctx = format_context(chunks)
    
    system_prompt = SYSTEM_BASE
    
    user_prompt = dedent(f"""
    [MODO] GROUNDED
    [PERGUNTA] {question}

    [TRECHOS SELECIONADOS]
    {ctx}

    Regras:
    - Responda SOMENTE com base nos trechos selecionados acima.
    - Sempre inclua uma seção final "Fontes consideradas" listando títulos/URLs usados.
    - Humanize a resposta (português natural), mas sem floreios desnecessários.
    - Se a resposta não estiver nos trechos, diga: "Não encontrei informação suficiente nos trechos recuperados."
    - Cite trechos específicos quando possível (ex: "Conforme o Trecho 2, ...").
    """)
    
    client = _get_client()
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    answer = response.choices[0].message.content
    
    logger.info("rag_grounded_done", answer_len=len(answer))
    
    return answer


def inference_answer(question: str, chunks: List[Dict[str, Any]], temperature: float = 0.2) -> str:
    """
    Generate inference answer (allows reasoning over chunks).
    
    Args:
        question: User question
        chunks: Retrieved chunks
        temperature: LLM temperature (0.2 for controlled creativity)
        
    Returns:
        Answer text
    """
    logger.info("rag_inference_start", question=question[:100], chunks=len(chunks))
    
    ctx = format_context(chunks)
    
    system_prompt = SYSTEM_BASE
    
    user_prompt = dedent(f"""
    [MODO] INFERENCE
    [PERGUNTA] {question}

    [TRECHOS SELECIONADOS]
    {ctx}

    Regras:
    - Responda com base nos trechos e, quando necessário, FAÇA INFERÊNCIAS explícitas.
    - Deixe claro quando algo é inferido (ex.: "Pela combinação dos artigos, infere-se que...").
    - Nunca cite fontes que não estejam na lista acima.
    - Sempre inclua uma seção final "Fontes consideradas" listando títulos/URLs usados.
    - Humanize a resposta (português natural).
    - Se precisar inferir além dos trechos, seja conservador e indique incerteza.
    """)
    
    client = _get_client()
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    answer = response.choices[0].message.content
    
    logger.info("rag_inference_done", answer_len=len(answer))
    
    return answer


def run_rag(
    question: str,
    mode: str = "grounded",
    top_k: int = 8,
    score_threshold: Optional[float] = None,
    collection: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run RAG pipeline: retrieve + answer.
    
    Args:
        question: User question
        mode: "grounded" or "infer"
        top_k: Number of chunks to retrieve
        score_threshold: Minimum score threshold
        collection: Collection name
        
    Returns:
        Dictionary with answer, log, and used chunks
    """
    from rag.retriever_qdrant import search_collection, DEFAULT_COLLECTION
    
    collection = collection or DEFAULT_COLLECTION
    
    logger.info("rag_run_start", question=question[:100], mode=mode, top_k=top_k)
    
    # Retrieve chunks
    hits = search_collection(
        query=question,
        top_k=top_k,
        collection=collection,
        score_threshold=score_threshold,
    )
    
    logger.info("rag_retrieved", hits=len(hits))
    
    # Log compacto para UI
    log = [{
        "doc_hash": h.get("doc_hash"),
        "chunk_id": h.get("chunk_id"),
        "score": h.get("score", 0.0),
        "title": h.get("title"),
        "url": h.get("url"),
        "source_type": h.get("source_type"),
        "anchor_type": h.get("anchor_type"),
    } for h in hits]
    
    # Select best 3-6 for context (to avoid token overflow)
    context_chunks = hits[:min(6, len(hits))]
    
    logger.info("rag_context_selected", chunks=len(context_chunks))
    
    # Generate answer based on mode
    if mode == "infer":
        answer = inference_answer(question, context_chunks)
    else:
        answer = grounded_answer(question, context_chunks)
    
    logger.info("rag_run_done", mode=mode, answer_len=len(answer))
    
    return {
        "answer": answer,
        "log": log,
        "used": [{
            "doc_hash": h.get("doc_hash"),
            "chunk_id": h.get("chunk_id"),
            "score": h.get("score", 0.0),
            "title": h.get("title"),
            "url": h.get("url"),
            "source_type": h.get("source_type"),
            "anchor_type": h.get("anchor_type"),
        } for h in context_chunks],
    }

