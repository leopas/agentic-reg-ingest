"""Smoke tests for UI console."""

from fastapi.testclient import TestClient

from apps.api.main import app


def test_ui_index_serves():
    """Test that UI console serves successfully."""
    client = TestClient(app)
    response = client.get("/ui")
    
    assert response.status_code == 200
    assert "Agentic Search Console" in response.text
    assert "htmx.org" in response.text


def test_ui_has_plan_section():
    """Test that UI has plan generation section."""
    client = TestClient(app)
    response = client.get("/ui")
    
    assert "Gerar Plano" in response.text
    assert "/agentic/plan" in response.text


def test_ui_has_run_section():
    """Test that UI has execution section."""
    client = TestClient(app)
    response = client.get("/ui")
    
    assert "Executar Loop" in response.text or "Executar" in response.text
    assert "/agentic/run" in response.text


def test_ui_has_iterations_section():
    """Test that UI has iterations/audit section."""
    client = TestClient(app)
    response = client.get("/ui")
    
    assert "Iterações" in response.text or "Audit" in response.text
    assert "/agentic/iters" in response.text


def test_root_includes_ui_link():
    """Test that root endpoint advertises UI."""
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "ui" in data or "ui_console" in data.get("endpoints", {})

