"""Claude Code headless integration — generate text via `claude -p`."""

import json
import shutil
import subprocess

from linkedin_post_generator.ai.exceptions import (
    AINotAvailableError,
    AIResponseError,
    AITimeoutError,
)

DEFAULT_TIMEOUT = 120
CLAUDE_CMD = "claude"


def is_headless_available() -> bool:
    """Check if Claude Code CLI is installed and accessible."""
    return shutil.which(CLAUDE_CMD) is not None


def generate_headless(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Generate text using Claude Code headless mode.

    Calls `claude -p --output-format json` with the prompt passed via stdin.

    Args:
        prompt: The full prompt to send to Claude.
        timeout: Maximum seconds to wait for response.

    Returns:
        Generated text from Claude.

    Raises:
        AINotAvailableError: If Claude CLI is not installed.
        AITimeoutError: If generation exceeds timeout.
        AIResponseError: If response is invalid or contains an error.
    """
    if not is_headless_available():
        raise AINotAvailableError(
            "Claude Code CLI not found. Install it from https://claude.ai/code"
        )

    try:
        result = subprocess.run(
            [CLAUDE_CMD, "-p", "--output-format", "json"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AITimeoutError(timeout) from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise AIResponseError(
            f"Claude CLI exited with code {result.returncode}: {stderr}"
        )

    return _parse_response(result.stdout)


def _parse_response(raw: str) -> str:
    """Parse JSON response from Claude headless and extract result text.

    Args:
        raw: Raw stdout from the claude CLI process.

    Returns:
        The generated text content.

    Raises:
        AIResponseError: If JSON is invalid or response indicates an error.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AIResponseError(f"Invalid JSON response from Claude: {exc}") from exc

    if data.get("is_error"):
        raise AIResponseError(f"Claude returned an error: {data.get('result', '')}")

    text = data.get("result")
    if not text:
        raise AIResponseError("Claude response missing 'result' field")

    return text
