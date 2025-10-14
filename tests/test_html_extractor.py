"""Tests for HTML extraction utilities."""

import pytest
from unittest.mock import Mock, patch

from agentic.html_extract import clean_html_to_excerpt, is_probably_pdf_wrapper


class TestCleanHTMLToExcerpt:
    """Test HTML cleaning and excerpt extraction."""
    
    def test_simple_html(self):
        """Test basic HTML extraction."""
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Main Title</h1>
            <h2>Subtitle</h2>
            <p>Some content here.</p>
            <table>
                <caption>Data Table</caption>
                <tr><td>Data</td></tr>
            </table>
        </body>
        </html>
        """
        
        result = clean_html_to_excerpt(html, "https://example.com", max_chars=10000)
        
        assert result["excerpt"]
        assert len(result["anchors_struct"]) >= 2  # At least h1, h2
        assert any(a["type"] == "h1" for a in result["anchors_struct"])
        assert any(a["type"] == "h2" for a in result["anchors_struct"])
        assert any(a["type"] == "table" for a in result["anchors_struct"])
    
    def test_pdf_links_detection(self):
        """Test PDF link extraction."""
        html = """
        <html>
        <body>
            <p>Download files:</p>
            <a href="document.pdf">PDF 1</a>
            <a href="/files/report.pdf">PDF 2</a>
            <a href="https://example.com/data.pdf?v=2">PDF 3</a>
        </body>
        </html>
        """
        
        result = clean_html_to_excerpt(html, "https://example.com/page", max_chars=10000)
        
        assert len(result["pdf_links"]) == 3
        # Check that links are absolute
        assert all(link.startswith("http") for link in result["pdf_links"])
    
    def test_script_removal(self):
        """Test that scripts and styles are removed."""
        html = """
        <html>
        <head>
            <script>alert('test');</script>
            <style>body { color: red; }</style>
        </head>
        <body>
            <h1>Clean Content</h1>
            <noscript>No script message</noscript>
        </body>
        </html>
        """
        
        result = clean_html_to_excerpt(html, "https://example.com", max_chars=10000)
        
        excerpt = result["excerpt"]
        assert "alert" not in excerpt
        assert "color: red" not in excerpt
        assert "Clean Content" in excerpt
    
    def test_max_chars_truncation(self):
        """Test that excerpt is truncated to max_chars."""
        html = "<body>" + ("x" * 100000) + "</body>"
        
        result = clean_html_to_excerpt(html, "https://example.com", max_chars=1000)
        
        assert len(result["excerpt"]) <= 1004  # 1000 + "..."


class TestIsProbablyPDFWrapper:
    """Test PDF wrapper detection."""
    
    def test_iframe_pdf(self):
        """Test detection of PDF in iframe."""
        html = """
        <html>
        <body>
            <iframe src="document.pdf"></iframe>
        </body>
        </html>
        """
        
        result = is_probably_pdf_wrapper(html, "https://example.com/page")
        
        assert result is not None
        assert result.endswith(".pdf")
    
    def test_embed_pdf(self):
        """Test detection of PDF in embed tag."""
        html = """
        <html>
        <body>
            <embed src="/files/report.pdf" type="application/pdf">
        </body>
        </html>
        """
        
        result = is_probably_pdf_wrapper(html, "https://example.com/page")
        
        assert result is not None
        assert "report.pdf" in result
    
    def test_meta_refresh_pdf(self):
        """Test detection of meta refresh to PDF."""
        html = """
        <html>
        <head>
            <meta http-equiv="refresh" content="0;URL=https://example.com/doc.pdf">
        </head>
        <body></body>
        </html>
        """
        
        result = is_probably_pdf_wrapper(html, "https://example.com/page")
        
        assert result is not None
        assert result.endswith(".pdf")
    
    def test_download_link_short_page(self):
        """Test detection of download link on short page."""
        html = """
        <html>
        <body>
            <h1>Download</h1>
            <a href="document.pdf">Baixar PDF</a>
        </body>
        </html>
        """
        
        result = is_probably_pdf_wrapper(html, "https://example.com/page")
        
        assert result is not None
        assert result.endswith(".pdf")
    
    def test_no_pdf_wrapper(self):
        """Test that normal HTML is not detected as wrapper."""
        html = """
        <html>
        <body>
            <h1>Article Title</h1>
            <p>This is a long article with lots of content.</p>
            <p>More paragraphs here making it longer.</p>
            <p>Even more content to ensure it's not short.</p>
            <a href="related.html">Related page</a>
        </body>
        </html>
        """
        
        result = is_probably_pdf_wrapper(html, "https://example.com/article")
        
        assert result is None
    
    def test_pdf_link_but_long_content(self):
        """Test that PDF links in long content don't trigger wrapper detection."""
        html = """
        <html>
        <body>
            <h1>Regulatory Document</h1>
            """ + ("<p>Content paragraph</p>\n" * 100) + """
            <p>See also: <a href="annex.pdf">Annex PDF</a></p>
        </body>
        </html>
        """
        
        result = is_probably_pdf_wrapper(html, "https://example.com/article")
        
        # Should not be detected as wrapper due to long content
        assert result is None

