# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LinkedIn Post Generator — interactive CLI tool that generates LinkedIn post drafts from sources (GitHub repos, article URLs, personal notes). AI-assisted, not AI-generated: the tool produces drafts, the user always reviews and refines.

**Key design decisions:**
- Fully interactive CLI flow (no flags/arguments required — everything through prompts)
- Dual AI backend: Claude Code headless (`claude -p --output-format json`) as primary, Anthropic API as fallback
- Cross-platform: Linux + macOS + Windows
- Bilingual posts: Polish and English
- Config with XDG-compliant paths and local override

## Tech Stack

- Python 3.12+ (managed with **uv**)
- **Typer** — CLI framework
- **Rich** — terminal UI (panels, tables, interactive prompts)
- **Claude Code headless** — primary AI backend (`claude -p --output-format json`)
- **anthropic** SDK — fallback AI backend (when ANTHROPIC_API_KEY is set)
- **httpx** — HTTP client for URL fetching
- **readability-lxml** — article content extraction (Mozilla Readability port)
- **Pydantic** — config validation
- **pyperclip** — cross-platform clipboard
- **pytest** — testing
- **ruff** — linting and formatting

## Commands

```bash
# Install dependencies
uv sync

# Run the CLI
uv run linkedin-post generate
uv run linkedin-post init
uv run linkedin-post config
uv run linkedin-post history

# Lint & format
uv run ruff check .
uv run ruff format .

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_foo.py::test_bar -v
```

## Architecture

### CLI Commands (Typer)
- `linkedin-post init` — first-run configuration wizard
- `linkedin-post generate` — fully interactive post generation (source → template → language → tone → length → generate → refine)
- `linkedin-post config` — interactive config editor
- `linkedin-post history` — history management (list, show, search, delete)

### Modules
- **CLI layer** (Typer + Rich) — interactive prompts, menus, output formatting
- **Source fetching** — httpx + readability for articles, GitHub REST API for repos, free-text input
- **AI backend** — Claude Code headless (primary) or Anthropic SDK (fallback). Auto-detects which is available
- **Templates** — 5 built-in post templates (Discovery, Opinion, TIL, Project Showcase, Article Reaction)
- **Config** — Pydantic model, TOML format, XDG paths (~/.config/linkedin-post/), local override
- **History** — SQLite database with deduplication, CRUD operations
- **Output** — Rich panel (terminal preview) + pyperclip (plain text clipboard) + optional .txt save

### Interactive Flow
1. Auto-init if no config exists
2. Source input (URL or free text)
3. Template selection (with Rich menu)
4. Language / tone / length selection (config provides defaults)
5. AI generation
6. Rich panel preview
7. Action menu: Copy to clipboard / Save / Refine / New version / Exit
8. Refinement loop (feedback → re-generate, keeping context)

### Config Location
- Global: `~/.config/linkedin-post/config.toml`
- Local override: `./config.toml`
- History DB: `~/.config/linkedin-post/history.db`

## Per-Directory CLAUDE.md

This root CLAUDE.md is kept under 200 lines — high-level architecture only.
Each module directory has its own `CLAUDE.md` with module-specific details (API contracts, internal conventions, data models).

Claude Code automatically loads CLAUDE.md from directories it works in, so you only get context relevant to the current task.

**Rule:** When `/start-work` creates a new directory, it MUST also create a `CLAUDE.md` in that directory describing the module's responsibility, public API, and internal conventions.

Planned module map:
- `linkedin_post_generator/` — package root, app wiring
- `linkedin_post_generator/cli/` — Typer commands, interactive prompts
- `linkedin_post_generator/fetcher/` — source fetching (URL, GitHub, text)
- `linkedin_post_generator/ai/` — AI backend (headless + API)
- `linkedin_post_generator/templates/` — post templates
- `linkedin_post_generator/config/` — Pydantic config, TOML reader
- `linkedin_post_generator/history/` — SQLite history, dedup
- `linkedin_post_generator/output/` — Rich panel, clipboard, file save

## Key Conventions

- Posts target 500–2000 characters depending on user choice (short/standard/long)
- Posts must sound human with personal perspective — never AI-slop
- LinkedIn accepts plain text only (no Markdown) — clipboard output is always plain text
- Config TOML format (native Python 3.12+ support, no extra dependency for reading)

## Linting

Run `uv run ruff check .` before every commit. Fix all issues — no `# noqa` without justification.

## Communication

When gathering requirements, making decisions, or clarifying ambiguities — always use the `AskUserQuestion` tool. This ensures structured, trackable conversations instead of free-form back-and-forth.
