"""Loader for user-defined templates stored as TOML files."""

import re
import tomllib
from pathlib import Path

from pydantic import BaseModel, ValidationError, field_validator

from linkedin_post_generator.templates.exceptions import TemplateError
from linkedin_post_generator.templates.models import CUSTOM_BADGE, PostTemplate
from linkedin_post_generator.templates.registry import TEMPLATES

_NAME_PATTERN = r"^[a-z0-9-]+$"


class _TemplateFile(BaseModel):
    """Schema of a single custom template TOML file."""

    name: str
    label: str
    description: str
    instructions: str

    @field_validator("name", "label", "description", "instructions")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("name")
    @classmethod
    def _slug(cls, value: str) -> str:
        if not re.fullmatch(_NAME_PATTERN, value):
            raise ValueError("must contain only a-z, 0-9 and '-'")
        return value


def load_custom_templates(directory: Path) -> list[PostTemplate]:
    """Load every ``*.toml`` template file from a directory.

    Files are read in name order. Each one becomes a PostTemplate with
    ``is_custom=True`` and its label prefixed with CUSTOM_BADGE.

    Args:
        directory: Directory holding the template files.

    Returns:
        The loaded templates; empty when the directory does not exist.

    Raises:
        TemplateError: If a file is not valid TOML, misses a field, has an
            empty or invalid field, or reuses the name of a built-in
            template or of another file.
    """
    if not directory.is_dir():
        return []

    templates: list[PostTemplate] = []
    seen: dict[str, Path] = {}
    for path in sorted(directory.glob("*.toml")):
        template = _load_file(path)
        if template.name in TEMPLATES:
            raise TemplateError(
                path, f"name '{template.name}' clashes with a built-in template"
            )
        if template.name in seen:
            raise TemplateError(
                path, f"name '{template.name}' is already used by {seen[template.name]}"
            )
        seen[template.name] = path
        templates.append(template)
    return templates


def _load_file(path: Path) -> PostTemplate:
    """Parse and validate one template file."""
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise TemplateError(path, f"invalid TOML ({e})") from e
    except UnicodeDecodeError as e:
        raise TemplateError(path, "file is not valid UTF-8") from e
    except OSError as e:
        raise TemplateError(path, f"cannot read file ({e.strerror})") from e

    try:
        parsed = _TemplateFile.model_validate(data)
    except ValidationError as e:
        raise TemplateError(path, _describe(e)) from e

    return PostTemplate(
        name=parsed.name,
        label=f"{CUSTOM_BADGE} {parsed.label}",
        description=parsed.description,
        instructions=parsed.instructions,
        is_custom=True,
    )


def _describe(error: ValidationError) -> str:
    """Turn a Pydantic validation error into a short, readable reason."""
    reasons = []
    for item in error.errors():
        field = ".".join(str(part) for part in item["loc"]) or "file"
        if item["type"] == "missing":
            reasons.append(f"missing field '{field}'")
        else:
            reasons.append(f"field '{field}': {item['msg']}")
    return "; ".join(reasons)
