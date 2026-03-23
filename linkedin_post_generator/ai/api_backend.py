"""Anthropic API fallback backend — generate text via the anthropic SDK."""

import os

import anthropic

from linkedin_post_generator.ai.exceptions import (
    AINotAvailableError,
    AIResponseError,
    AITimeoutError,
)

DEFAULT_TIMEOUT = 120
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MAX_TOKENS = 2048
ENV_KEY = "ANTHROPIC_API_KEY"


def is_api_available() -> bool:
    """Check if the Anthropic API key is set in the environment."""
    key = os.environ.get(ENV_KEY, "").strip()
    return len(key) > 0


def generate_api(
    prompt: str,
    system_prompt: str = "",
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Generate text using the Anthropic API.

    Args:
        prompt: The user message to send to Claude.
        system_prompt: Optional system message for role/context setup.
        timeout: Maximum seconds to wait for response.

    Returns:
        Generated text from Claude.

    Raises:
        AINotAvailableError: If ANTHROPIC_API_KEY is not set.
        AITimeoutError: If the API call exceeds timeout.
        AIResponseError: If the API returns an error or invalid response.
    """
    if not is_api_available():
        raise AINotAvailableError(
            f"{ENV_KEY} not set. Get an API key from https://console.anthropic.com/"
        )

    client = anthropic.Anthropic(timeout=float(timeout))

    try:
        message = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=DEFAULT_MAX_TOKENS,
            system=system_prompt or anthropic.NOT_GIVEN,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError as exc:
        raise AIResponseError(f"Invalid API key: {exc.message}") from exc
    except anthropic.RateLimitError as exc:
        raise AIResponseError(f"Rate limit exceeded: {exc.message}") from exc
    except anthropic.APITimeoutError as exc:
        raise AITimeoutError(timeout) from exc
    except anthropic.APIError as exc:
        raise AIResponseError(f"Anthropic API error: {exc.message}") from exc

    return _extract_text(message)


def _extract_text(message: anthropic.types.Message) -> str:
    """Extract text content from the API response.

    Args:
        message: The Message object from the API.

    Returns:
        The generated text.

    Raises:
        AIResponseError: If the response has no text content.
    """
    if not message.content:
        raise AIResponseError("API response has no content")

    for block in message.content:
        if block.type == "text":
            return block.text

    raise AIResponseError("API response has no text blocks")
