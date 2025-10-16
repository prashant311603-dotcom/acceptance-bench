"""Pytest configuration and fixtures."""

import pytest
import os
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key_12345")
    monkeypatch.setenv("BRIGHTSIDE_API_KEY", "test_key_67890")
    monkeypatch.setenv("BRIGHTSIDE_ENDPOINT", "https://test.example.com/api")
    monkeypatch.setenv("BRIGHTSIDE_MODEL_ID", "test-model")

