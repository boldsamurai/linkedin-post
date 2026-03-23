"""Tests for Anthropic API fallback backend."""

from unittest.mock import MagicMock, patch

import anthropic
import pytest

from linkedin_post_generator.ai.api_backend import generate_api, is_api_available
from linkedin_post_generator.ai.exceptions import (
    AINotAvailableError,
    AIResponseError,
    AITimeoutError,
)


def _make_text_block(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def _make_message(text: str = "Generated post content.") -> MagicMock:
    message = MagicMock(spec=anthropic.types.Message)
    message.content = [_make_text_block(text)]
    return message


class TestIsApiAvailable:
    """Check API key detection."""

    def test_available_when_key_set(self) -> None:
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test123"}):
            assert is_api_available() is True

    def test_unavailable_when_key_missing(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            assert is_api_available() is False

    def test_unavailable_when_key_empty(self) -> None:
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}):
            assert is_api_available() is False

    def test_unavailable_when_key_whitespace(self) -> None:
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "   "}):
            assert is_api_available() is False


class TestGenerateApiHappyPath:
    """Successful generation scenarios."""

    def test_returns_generated_text(self) -> None:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_message("My LinkedIn post")

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}),
            patch("anthropic.Anthropic", return_value=mock_client),
        ):
            result = generate_api("Write a post about Python")

        assert result == "My LinkedIn post"

    def test_passes_prompt_as_user_message(self) -> None:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_message()

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}),
            patch("anthropic.Anthropic", return_value=mock_client),
        ):
            generate_api("Write about decorators")

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["messages"] == [
            {"role": "user", "content": "Write about decorators"}
        ]

    def test_passes_system_prompt(self) -> None:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_message()

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}),
            patch("anthropic.Anthropic", return_value=mock_client),
        ):
            generate_api("Write a post", system_prompt="You are an editor")

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["system"] == "You are an editor"

    def test_sets_timeout_on_client(self) -> None:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_message()

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}),
            patch("anthropic.Anthropic", return_value=mock_client) as mock_cls,
        ):
            generate_api("test", timeout=60)

        mock_cls.assert_called_once_with(timeout=60.0)


class TestGenerateApiErrors:
    """Error handling scenarios."""

    def test_no_api_key_raises(self) -> None:
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(AINotAvailableError, match="ANTHROPIC_API_KEY not set"),
        ):
            generate_api("test prompt")

    def test_auth_error_raises(self) -> None:
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = anthropic.AuthenticationError(
            message="Invalid API key",
            response=MagicMock(status_code=401),
            body={"error": {"message": "Invalid API key"}},
        )

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-bad"}),
            patch("anthropic.Anthropic", return_value=mock_client),
            pytest.raises(AIResponseError, match="Invalid API key"),
        ):
            generate_api("test prompt")

    def test_rate_limit_raises(self) -> None:
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = anthropic.RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={"error": {"message": "Rate limit exceeded"}},
        )

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}),
            patch("anthropic.Anthropic", return_value=mock_client),
            pytest.raises(AIResponseError, match="Rate limit exceeded"),
        ):
            generate_api("test prompt")

    def test_timeout_raises(self) -> None:
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = anthropic.APITimeoutError(
            request=MagicMock(),
        )

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}),
            patch("anthropic.Anthropic", return_value=mock_client),
            pytest.raises(AITimeoutError, match="timed out after 120s"),
        ):
            generate_api("test prompt")

    def test_empty_content_raises(self) -> None:
        mock_client = MagicMock()
        message = MagicMock(spec=anthropic.types.Message)
        message.content = []
        mock_client.messages.create.return_value = message

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}),
            patch("anthropic.Anthropic", return_value=mock_client),
            pytest.raises(AIResponseError, match="no content"),
        ):
            generate_api("test prompt")

    def test_generic_api_error_raises(self) -> None:
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = anthropic.APIError(
            message="Server error",
            request=MagicMock(),
            body={"error": {"message": "Server error"}},
        )

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}),
            patch("anthropic.Anthropic", return_value=mock_client),
            pytest.raises(AIResponseError, match="Anthropic API error"),
        ):
            generate_api("test prompt")
