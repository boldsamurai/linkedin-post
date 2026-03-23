"""Data models for post templates."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PostTemplate:
    """A LinkedIn post template with instructions for AI generation.

    Attributes:
        name: Machine-readable identifier (e.g. "discovery").
        label: Human-readable name for menus (e.g. "Discovery").
        description: One-line description shown in template selection.
        instructions: Prompt snippet plugged into build_system_prompt().
    """

    name: str
    label: str
    description: str
    instructions: str
