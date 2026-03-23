"""AI backend — generate LinkedIn post text via Claude Code or Anthropic API."""

from linkedin_post_generator.ai.api_backend import generate_api, is_api_available
from linkedin_post_generator.ai.backend import detect_backend, generate
from linkedin_post_generator.ai.exceptions import (
    AIError,
    AINotAvailableError,
    AIResponseError,
    AITimeoutError,
)
from linkedin_post_generator.ai.headless import generate_headless, is_headless_available
from linkedin_post_generator.ai.prompt_builder import (
    build_system_prompt,
    build_user_message,
)

__all__ = [
    "AIError",
    "AINotAvailableError",
    "AIResponseError",
    "AITimeoutError",
    "build_system_prompt",
    "build_user_message",
    "detect_backend",
    "generate",
    "generate_api",
    "generate_headless",
    "is_api_available",
    "is_headless_available",
]
