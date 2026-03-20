# LinkedIn Post Generator

Interactive CLI tool that generates LinkedIn post drafts from various sources — GitHub repos, articles, or personal notes. AI-assisted, not AI-generated: you always review, refine, and approve before posting.

## Features

- **Fully interactive** — guided step-by-step flow, no flags to remember
- **Multiple sources** — GitHub repos, article URLs, or free-text notes
- **5 post templates** — Discovery, Opinion, TIL, Project Showcase, Article Reaction
- **Bilingual** — generate posts in Polish or English
- **Your voice** — configurable tone, style, hashtags, and post length
- **Iterative refinement** — tweak the draft until it's perfect
- **History tracking** — SQLite-backed history with dedup, search, and management
- **Cross-platform** — Linux, macOS, Windows

## Quick Start

```bash
# Install
uv sync

# First run — interactive setup wizard
uv run linkedin-post init

# Generate a post — fully interactive
uv run linkedin-post generate
```

The `generate` command walks you through:
1. Enter source (URL or text)
2. Pick a template
3. Choose language, tone, length
4. Review the draft
5. Copy / save / refine / regenerate

## Commands

| Command | Description |
|---------|-------------|
| `linkedin-post init` | First-run configuration wizard |
| `linkedin-post generate` | Interactive post generation |
| `linkedin-post config` | Edit your preferences |
| `linkedin-post history` | Browse, search, and manage past posts |

## Configuration

Personal preferences stored in `~/.config/linkedin-post/config.toml`:

```toml
# Default post language
language = "pl"

# Tone: professional-casual, technical, storytelling
tone = "professional-casual"

# Default post length: short (500-800), standard (800-1300), long (1300-2000)
length = "standard"

# Recurring hashtags
hashtags = ["#Python", "#SoftwareEngineering"]
```

## AI Backend

The tool supports two AI backends (auto-detected):

1. **Claude Code headless** (primary) — uses `claude -p` command. Requires [Claude Code](https://claude.ai/code) CLI installed.
2. **Anthropic API** (fallback) — uses `ANTHROPIC_API_KEY` environment variable. Requires an API key.

## Tech Stack

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/) (interactive CLI)
- [Claude Code](https://claude.ai/code) headless / [Anthropic SDK](https://docs.anthropic.com/)
- [httpx](https://www.python-httpx.org/) + [readability-lxml](https://github.com/buriy/python-readability) (content extraction)
- [Pydantic](https://docs.pydantic.dev/) (config validation)

## License

MIT
