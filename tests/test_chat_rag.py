# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Tests for Chat RAG functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock


def test_retriever_imports():
    """Test that retriever imports without errors."""
    from rag.retriever_qdrant import search_collection, embed_query, get_client
    
    # Should not raise
    assert callable(search_collection)
    assert callable(embed_query)
    assert callable(get_client)


def test_answerer_imports():
    """Test that answerer imports without errors."""
    from rag.answerer import run_rag, grounded_answer, inference_answer
    
    # Should not raise
    assert callable(run_rag)
    assert callable(grounded_answer)
    assert callable(inference_answer)


def test_chat_routes_imports():
    """Test that chat routes import without errors."""
    from apps.api.routes_chat import router, ChatAskRequest, ChatAskResponse
    
    # Should not raise
    assert router is not None
    assert ChatAskRequest is not None
    assert ChatAskResponse is not None


@patch('rag.retriever_qdrant.get_client')
@patch('rag.retriever_qdrant.embed_query')
def test_search_collection_mock(mock_embed, mock_client):
    """Test search_collection with mocked Qdrant."""
    # Mock embedding
    mock_embed.return_value = [0.1] * 1536
    
    # Mock search results
    mock_result = MagicMock()
    mock_result.id = 12345
    mock_result.score = 0.85
    mock_result.payload = {
        "text": "Test chunk",
        "doc_hash": "abc123",
        "chunk_id": "0",
        "url": "https://example.com",
        "title": "Test Doc",
        "source_type": "pdf",
    }
    
    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = [mock_result]
    mock_client.return_value = mock_qdrant
    
    from rag.retriever_qdrant import search_collection
    
    results = search_collection("test query", top_k=5)
    
    assert len(results) == 1
    assert results[0]["score"] == 0.85
    assert results[0]["text"] == "Test chunk"
    assert results[0]["doc_hash"] == "abc123"


@patch('rag.answerer._get_client')
@patch('rag.retriever_qdrant.search_collection')
def test_run_rag_grounded(mock_search, mock_openai):
    """Test RAG in grounded mode."""
    # Mock retrieval
    mock_search.return_value = [
        {
            "score": 0.9,
            "text": "Test chunk 1",
            "doc_hash": "abc",
            "chunk_id": "0",
            "url": "https://example.com",
            "title": "Doc 1",
            "source_type": "pdf",
            "anchor_type": None,
        }
    ]
    
    # Mock LLM
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Resposta baseada nos trechos.\n\nFontes: Doc 1"))]
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    from rag.answerer import run_rag
    
    result = run_rag("test question", mode="grounded", top_k=5)
    
    assert "answer" in result
    assert "log" in result
    assert "used" in result
    assert len(result["log"]) == 1
    assert "Resposta baseada" in result["answer"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

