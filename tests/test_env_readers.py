"""Tests for environment variable resolution in YAML configs."""

import os
import pytest
from pathlib import Path
from common.env_readers import _smart_cast, resolve_env_vars


class TestSmartCast:
    """Test smart type casting."""
    
    def test_cast_int(self):
        """Test integer casting."""
        assert _smart_cast("30") == 30
        assert _smart_cast("0") == 0
        assert _smart_cast("-5") == -5
        assert isinstance(_smart_cast("30"), int)
    
    def test_cast_float(self):
        """Test float casting."""
        assert _smart_cast("3.14") == 3.14
        assert _smart_cast("0.0") == 0.0
        assert isinstance(_smart_cast("3.14"), float)
    
    def test_cast_bool(self):
        """Test boolean casting."""
        # Note: "1" and "0" are cast to int, not bool
        # Only explicit bool strings are cast to bool
        assert _smart_cast("true") is True
        assert _smart_cast("True") is True
        assert _smart_cast("TRUE") is True
        assert _smart_cast("yes") is True
        
        assert _smart_cast("false") is False
        assert _smart_cast("False") is False
        assert _smart_cast("FALSE") is False
        assert _smart_cast("no") is False
    
    def test_cast_string(self):
        """Test string fallback."""
        assert _smart_cast("hello") == "hello"
        assert _smart_cast("sk-abc123") == "sk-abc123"
        assert isinstance(_smart_cast("hello"), str)


class TestResolveEnvVars:
    """Test environment variable resolution."""
    
    def test_resolve_full_placeholder_int(self, monkeypatch):
        """Test full placeholder with int value."""
        monkeypatch.setenv("TEST_TIMEOUT", "30")
        result = resolve_env_vars("${TEST_TIMEOUT}")
        assert result == 30
        assert isinstance(result, int)
    
    def test_resolve_full_placeholder_float(self, monkeypatch):
        """Test full placeholder with float value."""
        monkeypatch.setenv("TEST_TEMP", "0.5")
        result = resolve_env_vars("${TEST_TEMP}")
        assert result == 0.5
        assert isinstance(result, float)
    
    def test_resolve_full_placeholder_bool(self, monkeypatch):
        """Test full placeholder with bool value."""
        monkeypatch.setenv("TEST_ECHO", "true")
        result = resolve_env_vars("${TEST_ECHO}")
        assert result is True
        assert isinstance(result, bool)
    
    def test_resolve_full_placeholder_string(self, monkeypatch):
        """Test full placeholder with string value."""
        monkeypatch.setenv("TEST_API_KEY", "sk-abc123")
        result = resolve_env_vars("${TEST_API_KEY}")
        assert result == "sk-abc123"
        assert isinstance(result, str)
    
    def test_resolve_partial_placeholder(self, monkeypatch):
        """Test partial placeholder (stays as string)."""
        monkeypatch.setenv("TEST_PORT", "3306")
        result = resolve_env_vars("mysql://localhost:${TEST_PORT}/db")
        assert result == "mysql://localhost:3306/db"
        assert isinstance(result, str)
    
    def test_resolve_missing_var(self):
        """Test missing environment variable."""
        result = resolve_env_vars("${MISSING_VAR}")
        assert result == "${MISSING_VAR}"
    
    def test_resolve_dict(self, monkeypatch):
        """Test resolving nested dict."""
        monkeypatch.setenv("TEST_TIMEOUT", "30")
        monkeypatch.setenv("TEST_ECHO", "false")
        
        config = {
            "timeout": "${TEST_TIMEOUT}",
            "echo": "${TEST_ECHO}",
            "nested": {
                "value": "${TEST_TIMEOUT}"
            }
        }
        
        result = resolve_env_vars(config)
        assert result["timeout"] == 30
        assert result["echo"] is False
        assert result["nested"]["value"] == 30
    
    def test_resolve_list(self, monkeypatch):
        """Test resolving list."""
        monkeypatch.setenv("TEST_NUM", "42")
        
        config = ["${TEST_NUM}", "static", "${TEST_NUM}"]
        result = resolve_env_vars(config)
        
        assert result[0] == 42
        assert result[1] == "static"
        assert result[2] == 42

