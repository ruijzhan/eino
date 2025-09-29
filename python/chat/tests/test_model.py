"""Tests for model functionality."""

import pytest
import os
from unittest.mock import patch, MagicMock

from chat.model import (
    create_openai_chat_model,
    create_openai_chat_model_with_config,
    load_model_config,
    ModelConfig,
    default_model_config
)


def test_load_model_config_success():
    """Test successful model config loading from environment variables."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENAI_MODEL_NAME': 'gpt-4',
        'OPENAI_BASE_URL': 'https://api.test.com/v1',
        'OPENAI_TEMPERATURE': '0.5',
        'OPENAI_TIMEOUT': '60.0',
        'OPENAI_MAX_RETRIES': '5'
    }):
        config = load_model_config()

        assert config.api_key == 'test_key'
        assert config.model == 'gpt-4'
        assert config.base_url == 'https://api.test.com/v1'
        assert config.temperature == 0.5
        assert config.timeout == 60.0
        assert config.max_retries == 5


def test_load_model_config_missing_api_key():
    """Test model config loading with missing API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
            load_model_config()


def test_load_model_config_missing_model_name():
    """Test model config loading with missing model name."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key'
    }, clear=True):
        with pytest.raises(ValueError, match="OPENAI_MODEL_NAME environment variable is required"):
            load_model_config()


def test_load_model_config_invalid_temperature():
    """Test model config loading with invalid temperature."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENAI_MODEL_NAME': 'gpt-4',
        'OPENAI_TEMPERATURE': 'invalid'
    }):
        with pytest.raises(ValueError, match="Invalid OPENAI_TEMPERATURE value"):
            load_model_config()


def test_load_model_config_invalid_timeout():
    """Test model config loading with invalid timeout."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENAI_MODEL_NAME': 'gpt-4',
        'OPENAI_TIMEOUT': 'invalid'
    }):
        with pytest.raises(ValueError, match="Invalid OPENAI_TIMEOUT value"):
            load_model_config()


def test_load_model_config_invalid_max_retries():
    """Test model config loading with invalid max retries."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENAI_MODEL_NAME': 'gpt-4',
        'OPENAI_MAX_RETRIES': 'invalid'
    }):
        with pytest.raises(ValueError, match="Invalid OPENAI_MAX_RETRIES value"):
            load_model_config()


def test_load_model_config_negative_max_retries():
    """Test model config loading with negative max retries."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENAI_MODEL_NAME': 'gpt-4',
        'OPENAI_MAX_RETRIES': '-1'
    }):
        with pytest.raises(ValueError, match="OPENAI_MAX_RETRIES must be non-negative"):
            load_model_config()


def test_default_model_config():
    """Test default model configuration."""
    config = default_model_config()

    assert config.api_key == ""
    assert config.model == ""
    assert config.temperature == 0.7
    assert config.timeout == 30.0
    assert config.max_retries == 3


def test_create_openai_chat_model_with_custom_config():
    """Test model creation with custom config."""
    config = ModelConfig(
        api_key='test_key',
        model='gpt-4',
        base_url='https://api.test.com/v1',
        temperature=0.5
    )

    with patch('chat.model.ChatOpenAI') as mock_chat:
        mock_instance = MagicMock()
        mock_chat.return_value = mock_instance

        model = create_openai_chat_model_with_config(config)

        assert model == mock_instance
        mock_chat.assert_called_once_with(
            model='gpt-4',
            openai_api_key='test_key',
            openai_api_base='https://api.test.com/v1',
            temperature=0.5,
            request_timeout=30.0,
            max_retries=0
        )


def test_create_openai_chat_model_with_env_vars():
    """Test model creation using environment variables."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENAI_MODEL_NAME': 'gpt-4'
    }):
        with patch('chat.model.ChatOpenAI') as mock_chat:
            mock_instance = MagicMock()
            mock_chat.return_value = mock_instance

            model = create_openai_chat_model()

            assert model == mock_instance
            mock_chat.assert_called_once()
            # Check that the call was made with config loaded from env vars