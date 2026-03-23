"""Tests for Claude Code headless integration."""

import json
import subprocess
from unittest.mock import patch

import pytest

from linkedin_post_generator.ai.exceptions import (
    AINotAvailableError,
    AIResponseError,
    AITimeoutError,
)
from linkedin_post_generator.ai.headless import generate_headless, is_headless_available

SAMPLE_RESPONSE = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": "Here is your LinkedIn post draft about Python decorators.",
    "cost_usd": 0.003,
    "duration_ms": 1500,
    "num_turns": 1,
    "session_id": "abc123",
}


def _make_completed_process(
    stdout: str = "",
    stderr: str = "",
    returncode: int = 0,
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=["claude", "-p", "--output-format", "json"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class TestIsHeadlessAvailable:
    """Check CLI availability detection."""

    def test_available_when_claude_found(self) -> None:
        with patch("shutil.which", return_value="/usr/bin/claude"):
            assert is_headless_available() is True

    def test_unavailable_when_claude_missing(self) -> None:
        with patch("shutil.which", return_value=None):
            assert is_headless_available() is False


class TestGenerateHeadlessHappyPath:
    """Successful generation scenarios."""

    def test_returns_result_text(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(SAMPLE_RESPONSE)
            )
            result = generate_headless("Write a post about Python")

        assert result == SAMPLE_RESPONSE["result"]

    def test_passes_prompt_via_stdin(self) -> None:
        prompt = "Write a LinkedIn post about decorators"
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(SAMPLE_RESPONSE)
            )
            generate_headless(prompt)

        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs["input"] == prompt

    def test_uses_correct_cli_args(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(SAMPLE_RESPONSE)
            )
            generate_headless("test prompt")

        args = mock_run.call_args.args[0]
        assert args == ["claude", "-p", "--output-format", "json"]

    def test_includes_system_prompt_flag(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(SAMPLE_RESPONSE)
            )
            generate_headless("user msg", system_prompt="Be an editor")

        args = mock_run.call_args.args[0]
        assert "--system-prompt" in args
        idx = args.index("--system-prompt")
        assert args[idx + 1] == "Be an editor"

    def test_no_system_prompt_flag_when_empty(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(SAMPLE_RESPONSE)
            )
            generate_headless("user msg")

        args = mock_run.call_args.args[0]
        assert "--system-prompt" not in args

    def test_uses_shell_false(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(SAMPLE_RESPONSE)
            )
            generate_headless("test prompt")

        # subprocess.run does NOT receive shell=True
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs.get("shell") is not True


class TestGenerateHeadlessErrors:
    """Error handling scenarios."""

    def test_claude_not_installed_raises(self) -> None:
        with (
            patch("shutil.which", return_value=None),
            pytest.raises(AINotAvailableError, match="Claude Code CLI not found"),
        ):
            generate_headless("test prompt")

    def test_timeout_raises(self) -> None:
        side_effect = subprocess.TimeoutExpired("claude", 120)
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run", side_effect=side_effect),
            pytest.raises(AITimeoutError, match="timed out after 120s"),
        ):
            generate_headless("test prompt")

    def test_nonzero_exit_code_raises(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                returncode=1, stderr="Something went wrong"
            )
            with pytest.raises(AIResponseError, match="exited with code 1"):
                generate_headless("test prompt")

    def test_invalid_json_raises(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(stdout="not json at all")
            with pytest.raises(AIResponseError, match="Invalid JSON"):
                generate_headless("test prompt")

    def test_is_error_true_raises(self) -> None:
        error_response = {
            "type": "result",
            "is_error": True,
            "result": "Rate limit exceeded",
        }
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(error_response)
            )
            with pytest.raises(AIResponseError, match="Rate limit exceeded"):
                generate_headless("test prompt")

    def test_missing_result_field_raises(self) -> None:
        bad_response = {"type": "result", "is_error": False}
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(bad_response)
            )
            with pytest.raises(AIResponseError, match="missing 'result' field"):
                generate_headless("test prompt")

    def test_custom_timeout_passed_to_subprocess(self) -> None:
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = _make_completed_process(
                stdout=json.dumps(SAMPLE_RESPONSE)
            )
            generate_headless("test prompt", timeout=60)

        assert mock_run.call_args.kwargs["timeout"] == 60
