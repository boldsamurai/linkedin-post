"""Template lookup — built-in templates plus user-defined ones from disk."""

from linkedin_post_generator.config import paths
from linkedin_post_generator.templates.models import PostTemplate

# Registry of built-in templates only (populated by individual template modules);
# custom templates are read from templates_dir() on every lookup.
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
    """Get a built-in or custom template by name.

    Built-ins are resolved without reading the templates directory.

    Args:
        name: Template identifier (e.g. "discovery").

    Returns:
        The PostTemplate.

    Raises:
        KeyError: If no template with that name exists.
        TemplateError: If a custom template file is invalid.
    """
    if name in TEMPLATES:
        return TEMPLATES[name]
    templates = {t.name: t for t in list_templates()}
    try:
        return templates[name]
    except KeyError:
        available = ", ".join(sorted(templates))
        raise KeyError(f"Unknown template '{name}'. Available: {available}") from None


def list_templates() -> list[PostTemplate]:
    """List built-in templates in registration order, then custom ones.

    Returns:
        Built-in templates followed by templates loaded from templates_dir().

    Raises:
        TemplateError: If a custom template file is invalid.
    """
    # Imported here: custom_loader imports this module for the built-in names.
    from linkedin_post_generator.templates.custom_loader import load_custom_templates

    return list(TEMPLATES.values()) + load_custom_templates(paths.templates_dir())
