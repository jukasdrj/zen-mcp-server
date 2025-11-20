"""Tests for X.AI provider implementation."""

import os
from unittest.mock import MagicMock, patch

import pytest

from providers.shared import ProviderType
from providers.xai import XAIModelProvider


class TestXAIProvider:
    """Test X.AI provider functionality."""

    def setup_method(self):
        """Set up clean state before each test."""
        # Clear restriction service cache before each test
        import utils.model_restrictions

        utils.model_restrictions._restriction_service = None

    def teardown_method(self):
        """Clean up after each test to avoid singleton issues."""
        # Clear restriction service cache after each test
        import utils.model_restrictions

        utils.model_restrictions._restriction_service = None

    @patch.dict(os.environ, {"XAI_API_KEY": "test-key"})
    def test_initialization(self):
        """Test provider initialization."""
        provider = XAIModelProvider("test-key")
        assert provider.api_key == "test-key"
        assert provider.get_provider_type() == ProviderType.XAI
        assert provider.base_url == "https://api.x.ai/v1"

    def test_initialization_with_custom_url(self):
        """Test provider initialization with custom base URL."""
        provider = XAIModelProvider("test-key", base_url="https://custom.x.ai/v1")
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://custom.x.ai/v1"

    def test_model_validation(self):
        """Test model name validation."""
        provider = XAIModelProvider("test-key")

        # Test valid models and aliases - all resolve to grok-4-1-fast-non-reasoning
        assert provider.validate_model_name("grok-4-1-fast-non-reasoning") is True
        assert provider.validate_model_name("grok") is True
        assert provider.validate_model_name("grok4") is True
        assert provider.validate_model_name("grok41") is True
        assert provider.validate_model_name("grokfast") is True
        assert provider.validate_model_name("grokcode") is True
        assert provider.validate_model_name("grokheavy") is True
        assert provider.validate_model_name("grok-4-1-fast-non-reasoning-latest") is True

        # Test invalid model
        assert provider.validate_model_name("invalid-model") is False
        assert provider.validate_model_name("gpt-4") is False
        assert provider.validate_model_name("gemini-pro") is False

    def test_resolve_model_name(self):
        """Test model name resolution."""
        provider = XAIModelProvider("test-key")

        # Test shorthand resolution - all resolve to grok-4-1-fast-non-reasoning
        assert provider._resolve_model_name("grok") == "grok-4-1-fast-non-reasoning"
        assert provider._resolve_model_name("grok4") == "grok-4-1-fast-non-reasoning"
        assert provider._resolve_model_name("grok41") == "grok-4-1-fast-non-reasoning"
        assert provider._resolve_model_name("grokfast") == "grok-4-1-fast-non-reasoning"
        assert provider._resolve_model_name("grokcode") == "grok-4-1-fast-non-reasoning"
        assert provider._resolve_model_name("grokheavy") == "grok-4-1-fast-non-reasoning"

        # Test full name passthrough
        assert provider._resolve_model_name("grok-4-1-fast-non-reasoning") == "grok-4-1-fast-non-reasoning"
        assert provider._resolve_model_name("grok-4-1-fast-non-reasoning-latest") == "grok-4-1-fast-non-reasoning"

    def test_get_capabilities_grok_4_1_fast_non_reasoning(self):
        """Test getting model capabilities for Grok 4.1 Fast Non-Reasoning."""
        provider = XAIModelProvider("test-key")

        capabilities = provider.get_capabilities("grok-4-1-fast-non-reasoning")
        assert capabilities.model_name == "grok-4-1-fast-non-reasoning"
        assert capabilities.friendly_name == "X.AI (Grok 4.1 Fast Non-Reasoning)"
        assert capabilities.context_window == 2_000_000
        assert capabilities.provider == ProviderType.XAI
        assert not capabilities.supports_extended_thinking  # Non-reasoning variant
        assert capabilities.supports_system_prompts is True
        assert capabilities.supports_streaming is True
        assert capabilities.supports_function_calling is True
        assert capabilities.supports_json_mode is True
        assert capabilities.supports_images is True

        # Test temperature range
        assert capabilities.temperature_constraint.min_temp == 0.0
        assert capabilities.temperature_constraint.max_temp == 2.0
        assert capabilities.temperature_constraint.default_temp == 0.3

    def test_get_capabilities_with_shorthand(self):
        """Test getting model capabilities with shorthand."""
        provider = XAIModelProvider("test-key")

        capabilities = provider.get_capabilities("grok")
        assert capabilities.model_name == "grok-4-1-fast-non-reasoning"  # Should resolve to full name
        assert capabilities.context_window == 2_000_000

        capabilities_fast = provider.get_capabilities("grokfast")
        assert capabilities_fast.model_name == "grok-4-1-fast-non-reasoning"  # Should resolve to full name

    def test_unsupported_model_capabilities(self):
        """Test error handling for unsupported models."""
        provider = XAIModelProvider("test-key")

        with pytest.raises(ValueError, match="Unsupported model 'invalid-model' for provider xai"):
            provider.get_capabilities("invalid-model")

    def test_extended_thinking_flags(self):
        """X.AI capabilities should expose extended thinking support correctly."""
        provider = XAIModelProvider("test-key")

        # grok-4-1-fast-non-reasoning does NOT support extended thinking
        # It's the non-reasoning variant designed for instant responses
        non_thinking_aliases = ["grok-4-1-fast-non-reasoning", "grok", "grok4", "grokfast", "grokcode"]
        for alias in non_thinking_aliases:
            assert provider.get_capabilities(alias).supports_extended_thinking is False

    def test_provider_type(self):
        """Test provider type identification."""
        provider = XAIModelProvider("test-key")
        assert provider.get_provider_type() == ProviderType.XAI

    @patch.dict(os.environ, {"XAI_ALLOWED_MODELS": "grok-4-1-fast-non-reasoning"})
    def test_model_restrictions(self):
        """Test model restrictions functionality."""
        # Clear cached restriction service
        import utils.model_restrictions
        from providers.registry import ModelProviderRegistry

        utils.model_restrictions._restriction_service = None
        ModelProviderRegistry.reset_for_testing()

        provider = XAIModelProvider("test-key")

        # grok-4-1-fast-non-reasoning should be allowed
        assert provider.validate_model_name("grok-4-1-fast-non-reasoning") is True

        # Aliases that resolve to the canonical name ARE allowed (this is how restriction service works)
        assert provider.validate_model_name("grok") is True
        assert provider.validate_model_name("grok4") is True
        assert provider.validate_model_name("grokfast") is True

    @patch.dict(os.environ, {"XAI_ALLOWED_MODELS": "grok"})
    def test_multiple_model_restrictions(self):
        """Test multiple models in restrictions."""
        # Clear cached restriction service
        import utils.model_restrictions
        from providers.registry import ModelProviderRegistry

        utils.model_restrictions._restriction_service = None
        ModelProviderRegistry.reset_for_testing()

        provider = XAIModelProvider("test-key")

        # Shorthand "grok" should be allowed (resolves to grok-4-1-fast-non-reasoning)
        assert provider.validate_model_name("grok") is True

        # Full name should NOT be allowed (only shorthand "grok" is in restriction list)
        assert provider.validate_model_name("grok-4-1-fast-non-reasoning") is False

        # Other aliases should NOT be allowed
        assert provider.validate_model_name("grok4") is False
        assert provider.validate_model_name("grokfast") is False

    @patch.dict(os.environ, {"XAI_ALLOWED_MODELS": "grok,grok-4-1-fast-non-reasoning"})
    def test_both_shorthand_and_full_name_allowed(self):
        """Test that both shorthand and full name can be allowed."""
        # Clear cached restriction service
        import utils.model_restrictions

        utils.model_restrictions._restriction_service = None

        provider = XAIModelProvider("test-key")

        # Both shorthand and full name should be allowed
        assert provider.validate_model_name("grok") is True
        assert provider.validate_model_name("grok-4-1-fast-non-reasoning") is True

        # Other aliases that resolve to the canonical name are also allowed
        assert provider.validate_model_name("grokfast") is True
        assert provider.validate_model_name("grok4") is True

    @patch.dict(os.environ, {"XAI_ALLOWED_MODELS": ""})
    def test_empty_restrictions_allows_all(self):
        """Test that empty restrictions allow all models."""
        # Clear cached restriction service
        import utils.model_restrictions

        utils.model_restrictions._restriction_service = None

        provider = XAIModelProvider("test-key")

        # All aliases for the single model should be allowed
        assert provider.validate_model_name("grok-4-1-fast-non-reasoning") is True
        assert provider.validate_model_name("grok") is True
        assert provider.validate_model_name("grokfast") is True
        assert provider.validate_model_name("grok4") is True
        assert provider.validate_model_name("grokcode") is True

    def test_friendly_name(self):
        """Test friendly name constant."""
        provider = XAIModelProvider("test-key")
        assert provider.FRIENDLY_NAME == "X.AI"

        capabilities = provider.get_capabilities("grok-4-1-fast-non-reasoning")
        assert capabilities.friendly_name == "X.AI (Grok 4.1 Fast Non-Reasoning)"

    def test_supported_models_structure(self):
        """Test that MODEL_CAPABILITIES has the correct structure."""
        provider = XAIModelProvider("test-key")

        # Check that the single model is present
        assert "grok-4-1-fast-non-reasoning" in provider.MODEL_CAPABILITIES

        # Check model config has required fields
        from providers.shared import ModelCapabilities

        grok_config = provider.MODEL_CAPABILITIES["grok-4-1-fast-non-reasoning"]
        assert isinstance(grok_config, ModelCapabilities)
        assert hasattr(grok_config, "context_window")
        assert hasattr(grok_config, "supports_extended_thinking")
        assert hasattr(grok_config, "aliases")
        assert grok_config.context_window == 2_000_000
        assert grok_config.supports_extended_thinking is False  # Non-reasoning variant

        # Check aliases are correctly structured (model name itself is not in aliases)
        assert "grok" in grok_config.aliases
        assert "grok4" in grok_config.aliases
        assert "grokfast" in grok_config.aliases
        assert "grokcode" in grok_config.aliases
        assert "grok-4-1-fast-non-reasoning-latest" in grok_config.aliases

    @patch("providers.openai_compatible.OpenAI")
    def test_generate_content_resolves_alias_before_api_call(self, mock_openai_class):
        """Test that generate_content resolves aliases before making API calls.

        This is the CRITICAL test that ensures aliases like 'grok' get resolved
        to 'grok-4-1-fast-non-reasoning' before being sent to X.AI API.
        """
        # Set up mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock the completion response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "grok-4-1-fast-non-reasoning"  # API returns the resolved model name
        mock_response.id = "test-id"
        mock_response.created = 1234567890
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_client.chat.completions.create.return_value = mock_response

        provider = XAIModelProvider("test-key")

        # Call generate_content with alias 'grok'
        result = provider.generate_content(
            prompt="Test prompt",
            model_name="grok",
            temperature=0.7,  # This should be resolved to "grok-4-1-fast-non-reasoning"
        )

        # Verify the API was called with the RESOLVED model name
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]

        # CRITICAL ASSERTION: The API should receive "grok-4-1-fast-non-reasoning", not "grok"
        assert (
            call_kwargs["model"] == "grok-4-1-fast-non-reasoning"
        ), f"Expected 'grok-4-1-fast-non-reasoning' but API received '{call_kwargs['model']}'"

        # Verify other parameters
        assert call_kwargs["temperature"] == 0.7
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["messages"][0]["role"] == "user"
        assert call_kwargs["messages"][0]["content"] == "Test prompt"

        # Verify response
        assert result.content == "Test response"
        assert result.model_name == "grok-4-1-fast-non-reasoning"  # Should be the resolved name

    @patch("providers.openai_compatible.OpenAI")
    def test_generate_content_other_aliases(self, mock_openai_class):
        """Test other alias resolutions in generate_content."""
        from unittest.mock import MagicMock

        # Set up mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_client.chat.completions.create.return_value = mock_response

        provider = XAIModelProvider("test-key")

        # All aliases should resolve to grok-4-1-fast-non-reasoning
        mock_response.model = "grok-4-1-fast-non-reasoning"

        # Test grok4 -> grok-4-1-fast-non-reasoning
        provider.generate_content(prompt="Test", model_name="grok4", temperature=0.7)
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "grok-4-1-fast-non-reasoning"

        # Test full name -> grok-4-1-fast-non-reasoning
        provider.generate_content(prompt="Test", model_name="grok-4-1-fast-non-reasoning", temperature=0.7)
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "grok-4-1-fast-non-reasoning"

        # Test grokfast -> grok-4-1-fast-non-reasoning
        provider.generate_content(prompt="Test", model_name="grokfast", temperature=0.7)
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "grok-4-1-fast-non-reasoning"

        # Test grokcode -> grok-4-1-fast-non-reasoning
        provider.generate_content(prompt="Test", model_name="grokcode", temperature=0.7)
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "grok-4-1-fast-non-reasoning"
