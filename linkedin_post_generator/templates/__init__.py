"""Post templates — built-in LinkedIn post templates and prompt building."""

from linkedin_post_generator.templates.builder import build_prompt
from linkedin_post_generator.templates.models import PostTemplate
from linkedin_post_generator.templates.registry import (
    TEMPLATES,
    get_template,
    list_templates,
    register,
)

__all__ = [
    "TEMPLATES",
    "PostTemplate",
    "build_prompt",
    "get_template",
    "list_templates",
    "register",
]
