# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Tests for document router with DB-first strategy."""

import pytest
from unittest.mock import Mock, patch

from pipelines.routers import DocumentRouter


@pytest.fixture
def mock_llm():
    """Mock LLM client."""
    llm = Mock()
    llm.route_fallback = Mock(return_value="pdf")
    return llm


@pytest.fixture
def router(mock_llm):
    """Create DocumentRouter with mock LLM."""
    return DocumentRouter(mock_llm, timeout=20)


class TestRouteFromDB:
    """Test routing from DB final_type (highest priority)."""
    
    def test_route_pdf_from_db(self, router, mock_llm):
        """Test routing PDF when final_type is set in DB."""
        doc_type = router.route_item(
            url="https://example.com/doc.html",  # HTML extension (misleading)
            content_type="text/html",  # HTML content-type (misleading)
            title="Document",
            snippet="Content",
            final_type="pdf",  # Trust DB
        )
        
        assert doc_type == "pdf"
        # Should NOT call LLM or re-detect
        mock_llm.route_fallback.assert_not_called()
    
    def test_route_zip_from_db(self, router):
        """Test routing ZIP from DB."""
        doc_type = router.route_item(
            url="https://example.com/archive",
            final_type="zip",
        )
        assert doc_type == "zip"
    
    def test_route_html_from_db(self, router):
        """Test routing HTML from DB."""
        doc_type = router.route_item(
            url="https://example.com/page",
            final_type="html",
        )
        assert doc_type == "html"


class TestRedetectLive:
    """Test live re-detection when final_type is unknown."""
    
    @patch('agentic.detect.detect_type')
    @patch('requests.head')
    def test_redetect_when_unknown(self, mock_head, mock_detect, router, mock_llm):
        """Test re-detection when final_type is unknown."""
        # Mock HEAD response
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_head.return_value = mock_response
        
        # Mock detect_type
        mock_detect.return_value = {"final_type": "pdf"}
        
        doc_type = router.route_item(
            url="https://example.com/document",
            final_type="unknown",
        )
        
        assert doc_type == "pdf"
        mock_head.assert_called_once()
        mock_detect.assert_called_once()
        # Should NOT call LLM
        mock_llm.route_fallback.assert_not_called()
    
    @patch('agentic.detect.detect_type')
    @patch('requests.head')
    def test_redetect_when_missing(self, mock_head, mock_detect, router):
        """Test re-detection when final_type is None."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "text/html"}
        mock_head.return_value = mock_response
        
        mock_detect.return_value = {"final_type": "html"}
        
        doc_type = router.route_item(
            url="https://example.com/page",
            final_type=None,
        )
        
        assert doc_type == "html"
        mock_detect.assert_called_once()
    
    @patch('agentic.detect.detect_type')
    @patch('requests.head')
    def test_head_failure_fallback(self, mock_head, mock_detect, router):
        """Test fallback when HEAD fails."""
        mock_head.side_effect = Exception("Network error")
        mock_detect.return_value = {"final_type": "pdf"}
        
        doc_type = router.route_item(
            url="https://example.com/document.pdf",
            final_type="unknown",
        )
        
        # Should still detect (from URL extension)
        assert doc_type == "pdf"


class TestLLMFallback:
    """Test LLM fallback as last resort."""
    
    @patch('agentic.detect.detect_type')
    @patch('requests.head')
    def test_llm_fallback_when_redetect_unknown(self, mock_head, mock_detect, router, mock_llm):
        """Test LLM fallback when re-detection returns unknown."""
        mock_response = Mock()
        mock_response.headers = {}
        mock_head.return_value = mock_response
        
        mock_detect.return_value = {"final_type": "unknown"}
        mock_llm.route_fallback.return_value = "html"
        
        doc_type = router.route_item(
            url="https://example.com/unknown",
            title="Some Title",
            snippet="Some snippet",
            final_type="unknown",
        )
        
        # Should call LLM
        mock_llm.route_fallback.assert_called_once()
        assert doc_type == "html"
    
    def test_llm_invalid_output_defaults_html(self, router, mock_llm):
        """Test that invalid LLM output defaults to html."""
        mock_llm.route_fallback.return_value = "invalid_type"
        
        with patch('agentic.detect.detect_type') as mock_detect:
            with patch('requests.head') as mock_head:
                mock_head.return_value = Mock(headers={})
                mock_detect.return_value = {"final_type": "unknown"}
                
                doc_type = router.route_item(
                    url="https://example.com/unknown",
                    final_type="unknown",
                )
                
                assert doc_type == "html"  # Default fallback
    
    def test_llm_sanitization(self, router, mock_llm):
        """Test LLM output sanitization."""
        mock_llm.route_fallback.return_value = "  PDF  "  # Whitespace and uppercase
        
        with patch('agentic.detect.detect_type') as mock_detect:
            with patch('requests.head') as mock_head:
                mock_head.return_value = Mock(headers={})
                mock_detect.return_value = {"final_type": "unknown"}
                
                doc_type = router.route_item(
                    url="https://example.com/doc",
                    final_type="unknown",
                )
                
                assert doc_type == "pdf"  # Cleaned up


class TestBackwardCompatibility:
    """Test backward compatibility with legacy code."""
    
    @patch('agentic.detect.detect_type')
    @patch('requests.head')
    def test_legacy_call_without_final_type(self, mock_head, mock_detect, router):
        """Test routing without final_type parameter (legacy)."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_head.return_value = mock_response
        
        mock_detect.return_value = {"final_type": "pdf"}
        
        doc_type = router.route_item(
            url="https://example.com/document",
            content_type="application/pdf",
            title="Document",
            snippet="Content",
            # final_type not provided
        )
        
        assert doc_type == "pdf"

