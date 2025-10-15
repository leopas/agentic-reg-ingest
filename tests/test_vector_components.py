# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Tests for vector push components."""

import pytest
from unittest.mock import Mock, patch, MagicMock


def test_encoder_imports():
    """Test that encoder imports without errors."""
    from embeddings.encoder import encode_texts, get_embedding_dim
    
    # Should not raise
    dim = get_embedding_dim()
    assert dim > 0
    assert isinstance(dim, int)


def test_qdrant_client_imports():
    """Test that qdrant client imports without errors."""
    from vector.qdrant_client import get_client, ensure_collection
    
    # Should not raise
    assert get_client is not None
    assert ensure_collection is not None


def test_dao_chunk_helpers():
    """Test that DAO chunk helpers are defined."""
    from db.dao import (
        get_chunks_by_hashes,
        get_manifests_by_hashes,
        mark_manifest_vector,
    )
    
    # Functions should exist
    assert callable(get_chunks_by_hashes)
    assert callable(get_manifests_by_hashes)
    assert callable(mark_manifest_vector)


def test_pdf_ingestor_has_ingest_one():
    """Test that PDF ingestor has ingest_one method."""
    from pipelines.executors.pdf_ingestor import PDFIngestor
    
    # Check method exists
    assert hasattr(PDFIngestor, 'ingest_one')
    assert callable(getattr(PDFIngestor, 'ingest_one'))


def test_html_ingestor_has_ingest_one():
    """Test that HTML ingestor has ingest_one method."""
    from pipelines.executors.html_ingestor import HTMLIngestor
    
    # Check method exists
    assert hasattr(HTMLIngestor, 'ingest_one')
    assert callable(getattr(HTMLIngestor, 'ingest_one'))


def test_push_doc_hashes_signature():
    """Test that push_doc_hashes function exists with correct signature."""
    from vector.qdrant_loader import push_doc_hashes
    import inspect
    
    # Check function exists
    assert callable(push_doc_hashes)
    
    # Check signature
    sig = inspect.signature(push_doc_hashes)
    params = list(sig.parameters.keys())
    
    assert 'doc_hashes' in params
    assert 'collection' in params
    assert 'batch_size' in params
    assert 'overwrite' in params


@patch('embeddings.encoder.OpenAI')
def test_encode_texts_with_mock(mock_openai):
    """Test encode_texts with mocked OpenAI client."""
    # Mock response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1] * 1536),
        MagicMock(embedding=[0.2] * 1536),
    ]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    from embeddings.encoder import encode_texts
    
    # Mock environment
    with patch.dict('os.environ', {'EMBED_PROVIDER': 'openai', 'OPENAI_API_KEY': 'test-key'}):
        result = encode_texts(['text1', 'text2'])
    
    assert len(result) == 2
    assert len(result[0]) == 1536


def test_chunk_manifest_dao():
    """Test ChunkManifestDAO has required methods."""
    from db.dao import ChunkManifestDAO
    
    required_methods = [
        'find_by_doc_hash',
        'find_by_url',
        'upsert',
        'update_vector_status',
        'get_by_doc_hashes',
    ]
    
    for method_name in required_methods:
        assert hasattr(ChunkManifestDAO, method_name), f"Missing method: {method_name}"
        assert callable(getattr(ChunkManifestDAO, method_name))


def test_chunk_store_dao():
    """Test ChunkStoreDAO has required methods."""
    from db.dao import ChunkStoreDAO
    
    required_methods = [
        'create_chunk',
        'get_chunks_by_doc_hash',
        'delete_by_doc_hash',
        'bulk_create',
        'get_chunks_by_hashes',
    ]
    
    for method_name in required_methods:
        assert hasattr(ChunkStoreDAO, method_name), f"Missing method: {method_name}"
        assert callable(getattr(ChunkStoreDAO, method_name))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

