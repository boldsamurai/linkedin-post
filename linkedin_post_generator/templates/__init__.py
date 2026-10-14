"""Post templates — built-in LinkedIn post templates and prompt building."""

from linkedin_post_generator.templates import builtins as _builtins  # noqa: F401
from linkedin_post_generator.templates.builder import build_prompt
from linkedin_post_generator.templates.exceptions import TemplateError
from linkedin_post_generator.templates.models import CUSTOM_BADGE, PostTemplate
from linkedin_post_generator.templates.registry import (
    TEMPLATES,
    get_template,
    list_templates,
    register,
)

__all__ = [
    "CUSTOM_BADGE",
    "TEMPLATES",
    "PostTemplate",
    "TemplateError",
    "build_prompt",
    "get_template",
    "list_templates",
    "register",
]
