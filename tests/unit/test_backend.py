"""Tests for unified AI backend auto-detection and dispatch."""

from unittest.mock import patch

import pytest

from linkedin_post_generator.ai.backend import detect_backend, generate
from linkedin_post_generator.ai.exceptions import AINotAvailableError
from linkedin_post_generator.config.model import AIBackend

# Patch targets — the imported references in backend.py
_API_AVAILABLE = "linkedin_post_generator.ai.backend.is_api_available"
_HEADLESS_AVAILABLE = "linkedin_post_generator.ai.backend.is_headless_available"
_GENERATE_API = "linkedin_post_generator.ai.backend.generate_api"
_GENERATE_HEADLESS = "linkedin_post_generator.ai.backend.generate_headless"


class TestDetectBackendAuto:
    """AUTO mode: API key first, then headless, then error."""

    def test_prefers_api_when_key_set(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=True),
            patch(_HEADLESS_AVAILABLE, return_value=True),
        ):
            assert detect_backend(AIBackend.AUTO) == AIBackend.API

    def test_falls_back_to_headless(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=False),
            patch(_HEADLESS_AVAILABLE, return_value=True),
        ):
            assert detect_backend(AIBackend.AUTO) == AIBackend.HEADLESS

    def test_raises_when_nothing_available(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=False),
            patch(_HEADLESS_AVAILABLE, return_value=False),
            pytest.raises(AINotAvailableError, match="No AI backend available"),
        ):
            detect_backend(AIBackend.AUTO)

    def test_defaults_to_auto(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=True),
            patch(_HEADLESS_AVAILABLE, return_value=False),
        ):
            assert detect_backend() == AIBackend.API


class TestDetectBackendExplicit:
    """Explicit backend selection: validate availability."""

    def test_headless_available(self) -> None:
        with patch(_HEADLESS_AVAILABLE, return_value=True):
            assert detect_backend(AIBackend.HEADLESS) == AIBackend.HEADLESS

    def test_headless_missing_raises(self) -> None:
        with (
            patch(_HEADLESS_AVAILABLE, return_value=False),
            pytest.raises(AINotAvailableError, match="Claude Code CLI not found"),
        ):
            detect_backend(AIBackend.HEADLESS)

    def test_api_available(self) -> None:
        with patch(_API_AVAILABLE, return_value=True):
            assert detect_backend(AIBackend.API) == AIBackend.API

    def test_api_missing_raises(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=False),
            pytest.raises(AINotAvailableError, match="ANTHROPIC_API_KEY not set"),
        ):
            detect_backend(AIBackend.API)


class TestGenerate:
    """Unified generate() dispatches to correct backend."""

    def test_dispatches_to_api(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=True),
            patch(_GENERATE_API, return_value="API post") as mock_api,
        ):
            result = generate("Write a post", backend=AIBackend.API)

        assert result == "API post"
        mock_api.assert_called_once_with(
            prompt="Write a post", system_prompt="", timeout=120
        )

    def test_dispatches_to_headless(self) -> None:
        with (
            patch(_HEADLESS_AVAILABLE, return_value=True),
            patch(_GENERATE_HEADLESS, return_value="Headless post") as mock_hl,
        ):
            result = generate("Write a post", backend=AIBackend.HEADLESS)

        assert result == "Headless post"
        mock_hl.assert_called_once_with(prompt="Write a post", timeout=120)

    def test_auto_dispatches_to_api_when_available(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=True),
            patch(_HEADLESS_AVAILABLE, return_value=True),
            patch(_GENERATE_API, return_value="API result") as mock_api,
        ):
            result = generate("prompt", backend=AIBackend.AUTO)

        assert result == "API result"
        mock_api.assert_called_once()

    def test_passes_system_prompt_to_api(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=True),
            patch(_GENERATE_API, return_value="result") as mock_api,
        ):
            generate("prompt", system_prompt="Be an editor", backend=AIBackend.API)

        assert mock_api.call_args.kwargs["system_prompt"] == "Be an editor"

    def test_passes_custom_timeout(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=True),
            patch(_GENERATE_API, return_value="result") as mock_api,
        ):
            generate("prompt", backend=AIBackend.API, timeout=60)

        assert mock_api.call_args.kwargs["timeout"] == 60

    def test_raises_when_no_backend(self) -> None:
        with (
            patch(_API_AVAILABLE, return_value=False),
            patch(_HEADLESS_AVAILABLE, return_value=False),
            pytest.raises(AINotAvailableError),
        ):
            generate("prompt")
