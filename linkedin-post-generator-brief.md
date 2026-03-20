# LinkedIn Post Generator — Project Brief

## Idea
CLI tool that generates LinkedIn post drafts from a given source (GitHub repo, article URL, personal note). Uses Claude Code Headless command structure (no Claude API available) to create engaging, professional posts in the user's voice.

## Core Flow
1. User provides a source: URL (GitHub repo, blog post, article) or free-text note
2. Tool fetches/parses the source content
3. Claude generates a post draft based on a selected template
4. User reviews, edits, approves
5. Post is copied to clipboard or published via LinkedIn API

## Post Templates
- **Discovery** — "Found this tool/repo, here's why it's interesting"
- **Opinion** — "Here's my take on [topic/trend]"
- **TIL (Today I Learned)** — Short technical insight
- **Project showcase** — "I built X, here's what I learned"
- **Article reaction** — "Read this article, here's what stood out"

## Tech Stack
- Python
- Typer (CLI framework)
- Rich (terminal UI)
- Claude API (anthropic SDK)
- WebFetch for URL content extraction
- Pydantic for config/validation
- pytest for tests
- ruff for linting
- uv for package management

## Key Design Decisions
- AI-assisted, not AI-generated — the tool produces drafts, user always reviews
- Personal voice — configure tone, style, recurring hashtags in a config file
- Multiple output formats: clipboard, markdown file, direct LinkedIn API post
- Template system — extensible, user can add custom templates
- History — save generated posts to avoid repeating topics

## MVP Scope
1. CLI accepts a URL or text input
2. Fetches content from URL (GitHub README, article text)
3. Generates draft using Claude API with a selected template
4. Outputs to terminal + copies to clipboard
5. Config file for personal style preferences

## Future Ideas
- LinkedIn API integration for direct posting
- Scheduling (post queue)
- Analytics tracking (which posts performed best)
- Auto-suggest sources from RSS feeds or GitHub trending
- Image/banner generation for posts

## Important
- Posts must sound human, not AI-slop
- Always add personal perspective — "what I think about this", not just "here's a summary"
- Keep posts concise — LinkedIn sweet spot is 800-1300 characters
- Use formatting: line breaks, emojis (sparingly), bullet points
