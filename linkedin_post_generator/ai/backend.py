"""Unified AI backend — auto-detection and generation dispatch."""

from linkedin_post_generator.ai.api_backend import generate_api, is_api_available
from linkedin_post_generator.ai.exceptions import AINotAvailableError
from linkedin_post_generator.ai.headless import generate_headless, is_headless_available
from linkedin_post_generator.config.model import AIBackend

DEFAULT_TIMEOUT = 120


def detect_backend(preferred: AIBackend = AIBackend.AUTO) -> AIBackend:
    """Detect which AI backend to use.

    Detection order for AUTO:
        1. ANTHROPIC_API_KEY set → API
        2. claude CLI installed → headless
        3. Neither → raise AINotAvailableError

    For explicit backend choices (HEADLESS, API), validates availability.

    Args:
        preferred: Preferred backend from config. AUTO means auto-detect.

    Returns:
        The resolved AIBackend to use.

    Raises:
        AINotAvailableError: If the requested backend is not available.
    """
    if preferred == AIBackend.API:
        if is_api_available():
            return AIBackend.API
        raise AINotAvailableError(
            "ANTHROPIC_API_KEY not set. "
            "Get an API key from https://console.anthropic.com/"
        )

    if preferred == AIBackend.HEADLESS:
        if is_headless_available():
            return AIBackend.HEADLESS
        raise AINotAvailableError(
            "Claude Code CLI not found. Install it from https://claude.ai/code"
        )

    # AUTO: try API first, then headless
    if is_api_available():
        return AIBackend.API
    if is_headless_available():
        return AIBackend.HEADLESS

    raise AINotAvailableError(
        "No AI backend available. Either:\n"
        "  - Set ANTHROPIC_API_KEY environment variable, or\n"
        "  - Install Claude Code CLI from https://claude.ai/code"
    )


def generate(
    prompt: str,
    system_prompt: str = "",
    backend: AIBackend = AIBackend.AUTO,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Generate text using the best available AI backend.

    Args:
        prompt: The user message / full prompt.
        system_prompt: Optional system message for role/context setup.
        backend: Which backend to use (AUTO detects automatically).
        timeout: Maximum seconds to wait for response.

    Returns:
        Generated text from Claude.

    Raises:
        AINotAvailableError: If no backend is available.
        AITimeoutError: If generation exceeds timeout.
        AIResponseError: If the response is invalid or contains an error.
    """
    resolved = detect_backend(backend)

    if resolved == AIBackend.API:
        return generate_api(
            prompt=prompt,
            system_prompt=system_prompt,
            timeout=timeout,
        )

    return generate_headless(
        prompt=prompt, system_prompt=system_prompt, timeout=timeout
    )
