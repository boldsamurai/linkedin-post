---
globs: ["tests/**"]
---

# Testing Rules

## Structure
```
tests/
├── unit/              — isolated tests of single modules
│   ├── test_config.py
│   ├── test_fetcher.py
│   ├── test_ai_backend.py
│   ├── test_templates.py
│   └── test_history.py
├── integration/       — module collaboration tests
│   └── test_generate_flow.py
├── fixtures/          — test data
│   ├── html_pages/    — mock HTML for readability tests
│   └── api_responses/ — mock GitHub API / Claude responses
└── conftest.py        — shared fixtures
```

## AI in tests
- Unit and integration tests ALWAYS mock subprocess calls (Claude Code headless) and API calls (anthropic SDK)
- Never real AI calls in tests — tests must be deterministic and fast
- Mock responses in `tests/fixtures/` (JSON files or inline dicts)

## Fixtures
- `tmp_config_dir` — temporary config directory (pytest tmp_path)
- `sample_config` — AppConfig with example values
- `mock_claude_response` — simulated Claude Code JSON output
- `history_db` — temporary SQLite database
- Fixtures in `conftest.py`, not in individual test files

## Naming
- Files: `test_*.py`
- Functions: `test_<what>_<scenario>()`
- Example: `test_detect_source_type_github_url()`
- Example: `test_config_fallback_when_local_missing()`

## Assertions
- One concept per test — don't test 5 things in one function
- `assert` with clear message: `assert result.language == "pl", f"Expected pl, got {result.language}"`
- For exceptions: `with pytest.raises(ConfigError, match="Missing field")`

## HTTP mocking
- Use `pytest-httpx` for mocking httpx requests
- Or `respx` as alternative
- Always mock external HTTP calls — never hit real URLs in tests

## Coverage
- Meaningful scenarios over coverage numbers
- Every new function: happy path + at least one failure/edge case
- Bug fix → regression test first, then fix
