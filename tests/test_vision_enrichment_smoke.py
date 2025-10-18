# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Smoke tests for vision enrichment components."""

import pytest
from pathlib import Path

from agentic.vision.vision_client import VisionClient
from agentic.vision.gemini_client import GeminiClient
from agentic.enrichment.scraper import WebScraper
from ingestion.emitters.txt_emitter import TXTEmitter


def test_vision_client_init():
    """Test VisionClient initialization."""
    client = VisionClient(api_key="test_key")
    assert client.api_key == "test_key"


def test_gemini_client_init():
    """Test GeminiClient initialization."""
    client = GeminiClient(api_key="test_key", model="gemini-1.5-pro")
    assert client.api_key == "test_key"
    assert client.model == "gemini-1.5-pro"


def test_scraper_init():
    """Test WebScraper initialization."""
    scraper = WebScraper(timeout=30)
    assert scraper.timeout == 30


def test_txt_emitter_init(tmp_path):
    """Test TXTEmitter initialization."""
    emitter = TXTEmitter(output_base_dir=str(tmp_path))
    assert emitter.output_base_dir == tmp_path
    assert tmp_path.exists()


def test_txt_emitter_build_content():
    """Test TXTEmitter content building."""
    emitter = TXTEmitter(output_base_dir="/tmp/test")
    
    content = emitter._build_content_with_header(
        url="https://example.com",
        domain="example.com",
        fetched_at="2025-10-17T10:00:00Z",
        doc_hash="abc123",
        text="Test content"
    )
    
    assert "===META===" in content
    assert "url: https://example.com" in content
    assert "domain: example.com" in content
    assert "doc_hash: abc123" in content
    assert "===CONTENT===" in content
    assert "Test content" in content


def test_scraper_normalize_placeholder():
    """Test scraper HTML normalization (placeholder)."""
    scraper = WebScraper()
    
    # Test basic HTML parsing
    from bs4 import BeautifulSoup
    
    html = """
    <html>
        <head><title>Test</title></head>
        <body>
            <h1>Title</h1>
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
            <script>alert('test');</script>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html, "html.parser")
    normalized = scraper._normalize_html_to_text(soup)
    
    assert "TITLE" in normalized  # H1 should be uppercased
    assert "Paragraph 1" in normalized
    assert "Paragraph 2" in normalized
    assert "alert" not in normalized  # Scripts should be removed

