---
globs: ["linkedin_post_generator/**", "tests/**"]
---

# Python Style Rules

## Paths
- `pathlib.Path` everywhere — no `os.path.join()`, no manual slashes
- `Path / "subdir" / "file.toml"` — not `f"{dir}/subdir/file.toml"`
- Use `platformdirs` for XDG/cross-platform paths

## I/O
- Subprocess: list arguments + `shell=False`. Never `shell=True`
- CLI detection: `shutil.which("name")` — don't assume CLI is in PATH
- File encoding: always explicit `encoding="utf-8"` on open()

## Data classes
- Pydantic v2 for validation (config model, API responses)
- `dataclass` for simple DTOs
- `@dataclass(frozen=True)` for immutable value objects

## Typing
- Type hints on all public API (public functions, class methods)
- `str | None` not `Optional[str]` (Python 3.12+)
- `list[str]` not `List[str]`
- `dict[str, Any]` not `Dict[str, Any]`

## Error handling
- Custom exceptions over generic ones (e.g., `FetchError`, `ConfigError`)
- `try/except` around subprocess and file I/O — clear error messages
- Never bare `except:` — always specific exception type
- Fail fast — raise early, handle at CLI boundary

## Naming
- Files: snake_case (`source_fetcher.py`, `ai_backend.py`)
- Classes: PascalCase (`PostTemplate`, `HistoryStore`)
- Constants: UPPER_CASE (`DEFAULT_TONE`, `MAX_POST_LENGTH`)
- Private methods: `_prefix` (`_detect_source_type`, `_build_prompt`)
- Enums: PascalCase class, UPPER_CASE members

## Docstrings
- Google style
- Required on: classes, public methods, module-level functions
- Not required on: private methods (unless complex), tests

## Imports
- Absolute imports: `from linkedin_post_generator.config.model import AppConfig`
- Not: `from ..config import model`
- Grouping: stdlib → third-party → local (ruff sorts automatically)
