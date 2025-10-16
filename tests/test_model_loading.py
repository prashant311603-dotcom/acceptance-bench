"""Tests for model loading and registry."""

import pytest
import os
from unittest.mock import patch
from acceptance_bench.models import load_model, PROVIDER_DEFAULTS


def test_provider_defaults_exist():
    """Test that provider defaults are defined."""
    assert "openrouter" in PROVIDER_DEFAULTS
    assert "byo" in PROVIDER_DEFAULTS
    
    # OpenRouter should have expected defaults
    openrouter_defaults = PROVIDER_DEFAULTS["openrouter"]
    assert "endpoint" in openrouter_defaults
    assert "api_key_env" in openrouter_defaults
    assert openrouter_defaults["endpoint"] == "https://openrouter.ai/api/v1/chat/completions"


def test_load_model_requires_config():
    """Test that loading non-existent model raises error."""
    with pytest.raises(ValueError, match="not found in models.yaml"):
        load_model("nonexistent-model")


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"})
def test_load_openrouter_model():
    """Test loading an OpenRouter model."""
    # This should work without actual API calls
    model = load_model("grok-4")
    
    assert model is not None
    assert model.name == "grok-4"
    assert hasattr(model, 'provider')
    assert hasattr(model, 'generate')
    assert hasattr(model, 'validate_endpoint')


@patch.dict(os.environ, {
    "BRIGHTSIDE_API_KEY": "test_key",
    "BRIGHTSIDE_ENDPOINT": "https://test.com/api",
    "BRIGHTSIDE_MODEL_ID": "test-model"
})
def test_load_byo_model():
    """Test loading a BYO (custom) model."""
    model = load_model("brightside-v3")
    
    assert model is not None
    assert model.name == "brightside-v3"
    assert hasattr(model, 'provider')


def test_model_has_required_methods():
    """Test that models have required interface methods."""
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}):
        model = load_model("grok-4")
        
        # Should have these methods
        assert callable(getattr(model, 'generate', None))
        assert callable(getattr(model, 'validate_endpoint', None))


def test_openrouter_model_config():
    """Test that OpenRouter models get correct config."""
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}):
        model = load_model("grok-4")
        
        # Provider should have OpenRouter defaults
        assert model.provider.endpoint == "https://openrouter.ai/api/v1/chat/completions"
        assert model.provider.model_id == "x-ai/grok-4"

