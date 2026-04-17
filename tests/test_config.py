"""Tests for configuration module."""

import pytest
from pathlib import Path

from src.config import Settings


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()

    assert settings.default_ai_provider in ["nvidia", "openrouter"]
    assert isinstance(settings.watch_directory, Path)
    assert isinstance(settings.output_directory, Path)
    assert isinstance(settings.auto_save, bool)
    assert settings.max_file_size_mb > 0


def test_get_api_key():
    """Test getting API key for different providers."""
    settings = Settings(
        nvidia_api_key="test_nvidia_key",
        openrouter_api_key="test_openrouter_key",
    )

    assert settings.get_api_key("nvidia") == "test_nvidia_key"
    assert settings.get_api_key("openrouter") == "test_openrouter_key"


def test_get_api_key_invalid_provider():
    """Test getting API key for invalid provider."""
    settings = Settings()

    with pytest.raises(ValueError, match="Unknown provider"):
        settings.get_api_key("invalid")


def test_get_api_base():
    """Test getting API base URL for different providers."""
    settings = Settings()

    nvidia_base = settings.get_api_base("nvidia")
    openrouter_base = settings.get_api_base("openrouter")

    assert "nvidia" in nvidia_base.lower()
    assert "openrouter" in openrouter_base.lower()


def test_get_model():
    """Test getting model for different providers."""
    settings = Settings()

    nvidia_model = settings.get_model("nvidia")
    openrouter_model = settings.get_model("openrouter")

    assert isinstance(nvidia_model, str)
    assert isinstance(openrouter_model, str)
    assert len(nvidia_model) > 0
    assert len(openrouter_model) > 0
