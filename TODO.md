# TODO

This file tracks all tasks for the LinkedIn Post Generator project.
Tasks are grouped by feature area. Each task has sub-steps describing exactly what needs to be done.
Mark tasks with `[x]` when completed. This file is checked by the `/start-status` command.

## MVP

### Project Setup
- [ ] Initialize git repo
  - `git init`
  - Create initial commit with project scaffolding files
- [ ] Create project directory structure
  - `linkedin_post_generator/` — main package
  - `linkedin_post_generator/__init__.py`
  - `linkedin_post_generator/cli.py` — Typer app entry point
  - `tests/` — test directory
  - `tests/__init__.py`
  - `tests/conftest.py` — shared fixtures
- [ ] Install dependencies and verify environment
  - Run `uv sync`
  - Verify `uv run linkedin-post --help` works
  - Verify `uv run pytest` runs (even with 0 tests)
  - Verify `uv run ruff check .` passes

### Config System
- [ ] Define Pydantic config model
  - Fields: `language` (pl/en), `tone` (professional-casual/technical/storytelling), `length` (short/standard/long), `hashtags` (list[str]), `ai_backend` (auto/headless/api)
  - Use Pydantic `BaseModel` with validators and sensible defaults
  - Enum types for language, tone, length, ai_backend
- [ ] Implement TOML config reader
  - Use `tomllib` (stdlib Python 3.12+) for reading
  - Global path: `~/.config/linkedin-post/config.toml` (Linux/macOS), `%APPDATA%/linkedin-post/config.toml` (Windows)
  - Use `platformdirs` for cross-platform XDG path resolution
  - Create config directory if it doesn't exist
- [ ] Implement config fallback chain
  - Priority: local `./config.toml` > global `~/.config/linkedin-post/config.toml` > built-in defaults
  - Merge strategy: local overrides only the fields it defines, rest comes from global/defaults
- [ ] Write config to TOML file
  - Needed for `init` and `config` commands
  - Use `tomli-w` for writing (tomllib is read-only)
  - Preserve comments in existing config files where possible

### CLI Structure (Typer)
- [ ] Create Typer app with 4 commands
  - `init` — first-run configuration wizard
  - `generate` — interactive post generation
  - `config` — interactive config editor
  - `history` — history management with subcommands (list, show, search, delete)
  - `--version` flag on the main app
- [ ] Implement `init` command
  - Interactive wizard: ask for language, tone, length, hashtags
  - Detect AI backend availability (check `claude` CLI and ANTHROPIC_API_KEY)
  - Save config to global path
  - Print summary of saved settings
- [ ] Implement auto-init on `generate`
  - If no config file exists anywhere, run `init` wizard before proceeding
  - If config exists, skip and proceed to generation

### Source Fetching
- [ ] Implement URL content extraction
  - Use `httpx` for HTTP GET
  - Use `readability-lxml` to extract main article content (title + body text)
  - Strip HTML tags, return clean text
  - Handle errors: timeouts, 404s, non-HTML content
  - Set reasonable User-Agent header
- [ ] Implement GitHub repo fetching
  - Detect GitHub URLs (github.com/<owner>/<repo>)
  - Call GitHub REST API: `GET /repos/{owner}/{repo}` for metadata (description, stars, language, topics)
  - Call `GET /repos/{owner}/{repo}/readme` for README content (Accept: application/vnd.github.raw)
  - Optional: use GITHUB_TOKEN env var for higher rate limits (60/h without, 5000/h with)
  - Fallback: if API fails, fetch raw README from `raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md`
- [ ] Implement free-text note input
  - Rich prompt for multi-line text input
  - Support pasting from clipboard as source
- [ ] Implement source type auto-detection
  - Regex: `github.com/` → GitHub source
  - Regex: `http(s)://` → URL/article source
  - Everything else → free-text note

### AI Backend
- [ ] Implement Claude Code headless integration
  - Call `claude -p --output-format json` via `subprocess.run`
  - Parse JSON response: extract `result` field for post text
  - Handle errors: claude not installed, timeout, non-zero exit code
  - Pass prompt via stdin to avoid shell escaping issues
- [ ] Implement Anthropic API fallback
  - Use `anthropic` SDK with `ANTHROPIC_API_KEY` from env
  - Call `messages.create()` with the same prompt
  - Handle errors: invalid API key, rate limits, network errors
- [ ] Implement backend auto-detection
  - Check `ANTHROPIC_API_KEY` env var first → use API if set
  - Check `claude` CLI exists (`shutil.which("claude")`) → use headless
  - If neither available → error with installation instructions
- [ ] Design prompt templates
  - Base system prompt: "You are a LinkedIn post writer. Write in the user's voice, not AI-slop."
  - Per-template instructions (what to emphasize, what structure to follow)
  - Include user config context: tone, language, hashtags, target length
  - Include source content as user message

### Post Templates
- [ ] Implement template system
  - Template dataclass/model: name, description, system_prompt_snippet, example_structure
  - Registry of built-in templates
  - Function to build full prompt from template + source + config
- [ ] Discovery template
  - Focus: "I found this, here's why it matters to you"
  - Structure: hook → what it is → why it's interesting → call to action
  - Works best with GitHub repos and tool URLs
- [ ] Opinion template
  - Focus: "Here's my take, agree or disagree"
  - Structure: bold statement → context → argumentation → question to audience
  - Works best with free-text notes and article reactions
- [ ] TIL template
  - Focus: "Short, punchy technical insight"
  - Structure: "Today I learned..." → the insight → practical takeaway
  - Shorter format (500-800 chars ideal)
- [ ] Project Showcase template
  - Focus: "I built this, here's the journey"
  - Structure: problem → solution → what I learned → link
  - Works best with own GitHub repos
- [ ] Article Reaction template
  - Focus: "Read this, here's what stood out"
  - Structure: article reference → key insight → my perspective → recommendation
  - Works best with article URLs

### Interactive Flow
- [ ] Implement source input step
  - Rich prompt: "What do you want to write about?"
  - Detect source type from input
  - Fetch and preview source content (truncated summary)
  - Dedup check: warn if source URL exists in history
- [ ] Implement template selection
  - Rich interactive menu with all 5 templates
  - Each option shows: name + one-line description
  - Default from config (if set), otherwise no default
- [ ] Implement language selection
  - Options: Polski / English
  - Default from config
- [ ] Implement tone selection
  - Options: Professional-casual / Technical / Storytelling
  - Default from config
- [ ] Implement length selection
  - Options: Short (500-800) / Standard (800-1300) / Long (1300-2000)
  - Default from config
- [ ] Implement config defaults pre-fill
  - For each selection step: show config default as pre-selected option
  - User can confirm (Enter) or change

### Post Generation & Output
- [ ] Implement Rich panel display
  - Show generated post in a bordered Rich panel
  - Include metadata bar: template used, language, character count, word count
  - Syntax highlight hashtags and URLs within the post
- [ ] Implement clipboard copy
  - Use `pyperclip.copy()` with plain text (no Markdown, no Rich formatting)
  - Handle pyperclip errors (no clipboard mechanism on headless servers)
  - Show confirmation: "Copied to clipboard!"
- [ ] Implement file save
  - Save to .txt file with timestamp in filename: `linkedin-post-2026-03-20-143022.txt`
  - Default directory: current working directory
  - Include metadata header in file (date, source, template, language)
- [ ] Implement post-generation action menu
  - Rich prompt: "What next?"
  - Options: Copy to clipboard / Save to file / Refine this draft / Generate new version / Exit
  - Loop back to menu after each action (except Exit)

### Iterative Refinement
- [ ] Implement refinement prompt
  - After action menu → "Refine": ask "What should I change?"
  - Free-text input for feedback (e.g., "make shorter", "add more emoji", "less formal")
- [ ] Implement re-generation with context
  - Append user feedback to conversation context
  - For headless: build new prompt including original post + feedback
  - For API: use multi-turn messages array
  - Show new version in Rich panel
  - Return to action menu

### History (SQLite)
- [ ] Implement SQLite database
  - DB path: `~/.config/linkedin-post/history.db` (same dir as config)
  - Table `posts`: id (int PK autoincrement), created_at (datetime), source_type (text), source_url (text nullable), source_text (text), template (text), language (text), tone (text), post_text (text)
  - Auto-create table on first use
  - Use `sqlite3` stdlib module
- [ ] Implement save to history
  - Auto-save after successful generation (before action menu)
  - Store all metadata + full post text
- [ ] Implement deduplication check
  - Before generation: check if `source_url` already exists in history
  - If found: warn user with date and template of previous post, ask to continue or abort
- [ ] Implement `history` list command
  - Rich table: ID, date, source (truncated URL or first 50 chars of text), template, language
  - Paginate if >20 entries (show most recent first)
- [ ] Implement `history show <id>`
  - Display full post text in Rich panel (same format as generation output)
  - Show all metadata
- [ ] Implement `history search <query>`
  - SQL LIKE search across `source_url`, `source_text`, and `post_text`
  - Display results in same Rich table format as list
- [ ] Implement `history delete <id>`
  - Confirm before deletion: show post preview
  - Delete from database

### Tests
- [ ] Config tests
  - Loading from TOML file with all fields
  - Loading with partial fields (rest from defaults)
  - Fallback chain: local > global > defaults
  - Invalid config values (wrong enum, missing required)
  - Cross-platform path resolution
- [ ] Source fetching tests
  - Article extraction: mock httpx response with HTML, verify readability output
  - GitHub API: mock API response, verify metadata + README parsing
  - GitHub fallback: mock API failure, verify raw README fetch
  - Source type auto-detection: GitHub URL, article URL, plain text
  - Error handling: timeout, 404, non-HTML response
- [ ] AI backend tests
  - Headless: mock subprocess.run, verify JSON parsing
  - API: mock anthropic client, verify message construction
  - Auto-detection: test with/without ANTHROPIC_API_KEY and claude CLI
  - Error handling: missing backend, timeout, invalid response
- [ ] Template tests
  - Each template produces valid prompt with required sections
  - Prompt includes source content, config values, language instruction
  - Character count targets are included in prompt
- [ ] History tests
  - CRUD: create, read, search, delete
  - Deduplication: detect existing source URL
  - Empty database handling
  - Search with no results
- [ ] CLI tests
  - Smoke test: `--help` works for all commands
  - Init wizard: mock prompts, verify config file created
  - Generate flow: mock AI backend, verify interactive prompts fire in order
  - History subcommands: verify output format

## Post-MVP

### LinkedIn API Integration
- [ ] OAuth2 flow for LinkedIn authentication
  - Register LinkedIn Developer App
  - Implement OAuth2 authorization code flow
  - Store access token securely (keyring or encrypted config)
  - Handle token refresh
- [ ] Direct post publishing from CLI
  - Use LinkedIn UGC Post API (or Share API v2)
  - Action menu option: "Publish to LinkedIn"
  - Confirmation prompt before publishing
  - Show post URL after successful publish

### Custom Templates
- [ ] User-defined templates
  - Template format: TOML file in `~/.config/linkedin-post/templates/`
  - Fields: name, description, system_prompt, example_structure
  - Validation on load (required fields, prompt sanity check)
- [ ] Template discovery and selection
  - Scan built-in + custom templates directory
  - Show custom templates alongside built-in in selection menu
  - Mark custom templates with a badge/icon

### Scheduling & Queue
- [ ] Post queue with planned publish dates
  - SQLite table for scheduled posts
  - CLI: `linkedin-post schedule` — pick post from history + set date/time
- [ ] Scheduler daemon
  - Cron job or lightweight daemon
  - Auto-publish when scheduled time arrives (requires LinkedIn API)

### Analytics
- [ ] Post performance tracking
  - Manual input: `linkedin-post analytics log <id> --likes N --comments N`
  - Or automatic via LinkedIn API (if integrated)
- [ ] Insights
  - Best performing templates
  - Optimal posting times (based on historical data)

### Advanced Sources
- [ ] RSS feed integration
  - Configure RSS feeds in config
  - `linkedin-post suggest` — fetch latest articles, suggest topics
- [ ] GitHub trending
  - Fetch trending repos for user's languages
  - Suggest as post sources
- [ ] Image/banner generation
  - Generate Open Graph-style images for posts
  - Use Pillow or external service
