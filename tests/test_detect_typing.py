"""Tests for robust document type detection."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from agentic.detect import (
    _url_ext,
    _sniff_magic,
    _detect_from_magic,
    _detect_from_disposition,
    _detect_from_content_type,
    detect_type,
)


class TestUrlExt:
    """Test URL extension extraction."""
    
    def test_pdf_extension(self):
        """Test PDF extension detection."""
        assert _url_ext("https://example.com/document.pdf") == "pdf"
        assert _url_ext("https://example.com/path/to/file.PDF") == "pdf"
    
    def test_zip_extension(self):
        """Test ZIP extension detection."""
        assert _url_ext("https://example.com/archive.zip") == "zip"
    
    def test_html_extension(self):
        """Test HTML extension detection."""
        assert _url_ext("https://example.com/page.html") == "html"
        assert _url_ext("https://example.com/page.htm") == "htm"
    
    def test_query_params_ignored(self):
        """Test that query params don't affect extension."""
        assert _url_ext("https://example.com/file.pdf?version=2") == "pdf"
        assert _url_ext("https://example.com/file.pdf#section") == "pdf"
    
    def test_no_extension(self):
        """Test URLs without extension."""
        assert _url_ext("https://example.com/document") is None
        assert _url_ext("https://example.com/") is None
    
    def test_unknown_extension(self):
        """Test unknown extensions."""
        assert _url_ext("https://example.com/file.unknown") is None


class TestDetectFromMagic:
    """Test magic bytes detection."""
    
    def test_pdf_magic(self):
        """Test PDF magic bytes."""
        assert _detect_from_magic(b'%PDF-1.4\x00\x00\x00\x00') == "pdf"
        assert _detect_from_magic(b'%PDF-1.7') == "pdf"
    
    def test_zip_magic(self):
        """Test ZIP magic bytes."""
        assert _detect_from_magic(b'PK\x03\x04abcd') == "zip"
        assert _detect_from_magic(b'PK\x05\x06abcd') == "zip"
        assert _detect_from_magic(b'PK\x07\x08abcd') == "zip"
    
    def test_unknown_magic(self):
        """Test unknown magic bytes."""
        assert _detect_from_magic(b'UNKNOWN\x00') is None
        assert _detect_from_magic(b'') is None
        assert _detect_from_magic(b'abc') is None


class TestDetectFromDisposition:
    """Test Content-Disposition parsing."""
    
    def test_pdf_filename(self):
        """Test PDF filename in disposition."""
        assert _detect_from_disposition('attachment; filename="document.pdf"') == "pdf"
        assert _detect_from_disposition('inline; filename=report.pdf') == "pdf"
    
    def test_zip_filename(self):
        """Test ZIP filename in disposition."""
        assert _detect_from_disposition('attachment; filename="archive.zip"') == "zip"
    
    def test_html_filename(self):
        """Test HTML filename in disposition."""
        assert _detect_from_disposition('attachment; filename="page.html"') == "html"
        assert _detect_from_disposition('attachment; filename="index.htm"') == "html"
    
    def test_url_encoded_filename(self):
        """Test URL-encoded filename."""
        assert _detect_from_disposition('attachment; filename="file%20name.pdf"') == "pdf"
    
    def test_no_disposition(self):
        """Test missing disposition."""
        assert _detect_from_disposition(None) is None
        assert _detect_from_disposition('') is None
    
    def test_no_filename(self):
        """Test disposition without filename."""
        assert _detect_from_disposition('attachment') is None


class TestDetectFromContentType:
    """Test Content-Type detection."""
    
    def test_pdf_content_type(self):
        """Test PDF Content-Type."""
        assert _detect_from_content_type("application/pdf", None) == "pdf"
        assert _detect_from_content_type("application/PDF; charset=utf-8", None) == "pdf"
    
    def test_zip_content_type(self):
        """Test ZIP Content-Type."""
        assert _detect_from_content_type("application/zip", None) == "zip"
        assert _detect_from_content_type("application/x-zip-compressed", None) == "zip"
    
    def test_html_content_type(self):
        """Test HTML Content-Type."""
        assert _detect_from_content_type("text/html", None) == "html"
        assert _detect_from_content_type("text/html; charset=utf-8", None) == "html"
    
    def test_text_with_html_extension(self):
        """Test text/* with HTML extension."""
        assert _detect_from_content_type("text/plain", "html") == "html"
    
    def test_html_but_pdf_extension(self):
        """Test HTML Content-Type but PDF URL - trust extension."""
        assert _detect_from_content_type("text/html", "pdf") == "pdf"
    
    def test_no_content_type(self):
        """Test missing Content-Type."""
        assert _detect_from_content_type(None, None) is None
        assert _detect_from_content_type("", None) is None


class TestDetectType:
    """Test full type detection."""
    
    @patch('agentic.detect._sniff_magic')
    def test_magic_bytes_priority(self, mock_sniff):
        """Test that magic bytes have highest priority."""
        mock_sniff.return_value = b'%PDF-1.4'
        
        result = detect_type(
            "https://example.com/document.html",  # HTML extension
            {"Content-Type": "text/html"},  # HTML content-type
            sniff_magic=True,
        )
        
        assert result["final_type"] == "pdf"
        assert result["fetch_status"] == "ok"
    
    @patch('agentic.detect._sniff_magic')
    def test_disposition_priority(self, mock_sniff):
        """Test Content-Disposition priority over Content-Type."""
        mock_sniff.return_value = None
        
        result = detect_type(
            "https://example.com/document",
            {
                "Content-Type": "text/html",
                "Content-Disposition": 'attachment; filename="report.pdf"',
            },
            sniff_magic=True,
        )
        
        assert result["final_type"] == "pdf"
    
    @patch('agentic.detect._sniff_magic')
    def test_content_type_priority(self, mock_sniff):
        """Test Content-Type detection."""
        mock_sniff.return_value = None
        
        result = detect_type(
            "https://example.com/document.html",
            {"Content-Type": "application/pdf"},
            sniff_magic=True,
        )
        
        assert result["final_type"] == "pdf"
        assert result["detected_mime"] == "application/pdf"
    
    @patch('agentic.detect._sniff_magic')
    def test_url_extension_fallback(self, mock_sniff):
        """Test URL extension as fallback."""
        mock_sniff.return_value = None
        
        result = detect_type(
            "https://example.com/document.pdf",
            {},
            sniff_magic=True,
        )
        
        assert result["final_type"] == "pdf"
    
    @patch('agentic.detect._sniff_magic')
    def test_unknown_fallback(self, mock_sniff):
        """Test unknown fallback."""
        mock_sniff.return_value = None
        
        result = detect_type(
            "https://example.com/document",
            {},
            sniff_magic=True,
        )
        
        assert result["final_type"] == "unknown"
    
    def test_no_sniff(self):
        """Test detection without magic sniffing."""
        result = detect_type(
            "https://example.com/document.pdf",
            {"Content-Type": "application/pdf"},
            sniff_magic=False,
        )
        
        assert result["final_type"] == "pdf"
    
    @patch('agentic.detect._sniff_magic')
    def test_zip_magic_bytes(self, mock_sniff):
        """Test ZIP detection via magic bytes."""
        mock_sniff.return_value = b'PK\x03\x04'
        
        result = detect_type(
            "https://example.com/archive",
            {},
            sniff_magic=True,
        )
        
        assert result["final_type"] == "zip"


class TestSniffMagic:
    """Test magic bytes sniffing."""
    
    @patch('requests.get')
    def test_successful_sniff(self, mock_get):
        """Test successful magic bytes fetch."""
        mock_response = Mock()
        mock_response.status_code = 206
        mock_response.iter_content = Mock(return_value=[b'%PDF-1.4'])
        mock_response.close = Mock()
        mock_get.return_value = mock_response
        
        result = _sniff_magic("https://example.com/file.pdf")
        
        assert result == b'%PDF-1.4'
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_failed_sniff(self, mock_get):
        """Test failed magic bytes fetch."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = _sniff_magic("https://example.com/file.pdf")
        
        assert result is None
    
    @patch('requests.get')
    def test_404_response(self, mock_get):
        """Test 404 response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = _sniff_magic("https://example.com/file.pdf")
        
        assert result is None

