"""Built-in post template definitions and lookup."""

from linkedin_post_generator.templates.models import PostTemplate

# Registry of all built-in templates (populated by individual template modules)
TEMPLATES: dict[str, PostTemplate] = {}


def register(template: PostTemplate) -> PostTemplate:
    """Register a template in the global registry.

    Args:
        template: The PostTemplate to register.

    Returns:
        The same template (for use as inline registration).
    """
    TEMPLATES[template.name] = template
    return template


def get_template(name: str) -> PostTemplate:
    """Get a template by name.

    Args:
        name: Template identifier (e.g. "discovery").

    Returns:
        The PostTemplate.

    Raises:
        KeyError: If no template with that name exists.
    """
    try:
        return TEMPLATES[name]
    except KeyError:
        available = ", ".join(sorted(TEMPLATES.keys()))
        raise KeyError(f"Unknown template '{name}'. Available: {available}") from None


def list_templates() -> list[PostTemplate]:
    """List all available templates in registration order.

    Returns:
        List of all registered PostTemplates.
    """
    return list(TEMPLATES.values())
