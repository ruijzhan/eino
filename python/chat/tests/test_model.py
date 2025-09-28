"""Tests for model functionality."""

import pytest
import os
from unittest.mock import patch, MagicMock

from model import create_openai_chat_model


def test_create_openai_chat_model_success():
    """Test successful model creation with environment variables."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENAI_MODEL_NAME': 'gpt-4',
        'OPENAI_BASE_URL': 'https://api.test.com/v1'
    }):
        model = create_openai_chat_model()

        assert model is not None
        assert model.model_name == 'gpt-4'
        assert model.openai_api_key == 'test_key'
        assert model.openai_api_base == 'https://api.test.com/v1'
        assert model.temperature == 0.0


def test_create_openai_chat_model_missing_api_key():
    """Test model creation with missing API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
            create_openai_chat_model()


def test_create_openai_chat_model_custom_params():
    """Test model creation with custom parameters."""
    model = create_openai_chat_model(
        api_key='custom_key',
        model_name='gpt-3.5-turbo',
        base_url='https://custom.api.com/v1',
        temperature=0.7
    )

    assert model is not None
    assert model.model_name == 'gpt-3.5-turbo'
    assert model.openai_api_key == 'custom_key'
    assert model.openai_api_base == 'https://custom.api.com/v1'
    assert model.temperature == 0.7


def test_create_openai_chat_model_defaults():
    """Test model creation with default values."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key'
    }):
        model = create_openai_chat_model()

        assert model is not None
        assert model.model_name == 'gpt-3.5-turbo'  # Default
        assert model.openai_api_key == 'test_key'
        assert model.openai_api_base is None  # Default
        assert model.temperature == 0.0  # Default