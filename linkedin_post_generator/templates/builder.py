"""Prompt builder — combines templates with config to produce ready prompts."""

from linkedin_post_generator.ai.prompt_builder import (
    build_system_prompt,
    build_user_message,
)
from linkedin_post_generator.config.model import Language, Length, Tone
from linkedin_post_generator.templates.registry import get_template


def build_prompt(
    template_name: str,
    source_content: str,
    tone: Tone,
    language: Language,
    length: Length,
    hashtags: list[str] | None = None,
) -> tuple[str, str]:
    """Build a complete (system_prompt, user_message) pair for generation.

    Resolves the template by name and combines it with user config
    to produce prompts ready to pass to the AI backend.

    Args:
        template_name: Template identifier (e.g. "discovery").
        source_content: Fetched source text (article, README, note).
        tone: Writing tone from config.
        language: Target language from config.
        length: Target post length from config.
        hashtags: Default hashtags from config.

    Returns:
        Tuple of (system_prompt, user_message).
    """
    template = get_template(template_name)

    system = build_system_prompt(
        template_instructions=template.instructions,
        tone=tone,
        language=language,
        length=length,
        hashtags=hashtags,
    )
    user = build_user_message(source_content)

    return system, user
