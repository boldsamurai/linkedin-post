# Decision log

Append-only. Newest at the bottom. Each entry: date, decision, why.

## 2026-10-14 — RSS parsing with feedparser

- **Decision:** parse RSS/Atom with `feedparser`; httpx downloads the feed, feedparser only gets the bytes.
- **Why:** tolerant of real-world broken feeds, RSS and Atom variants and date formats; HTTP stays mockable with pytest-httpx.
- **Given up:** zero new dependencies (stdlib `xml.etree` would mean our own parser and more edge cases to test).

## 2026-10-14 — `suggest` hands the picked entry to `generate`

- **Decision:** `linkedin-post suggest` lists recent feed entries (used ones marked from history), and the picked one starts the generate flow with its URL as the source.
- **Why:** one continuous flow from discovery to draft, with dedup and preview reused instead of copy-pasting URLs.
- **Given up:** AI-proposed topics; `generate_cmd.py` has to accept a preset source (refactor in lane B).

## 2026-10-14 — Custom templates: badge in the label, fail fast on broken files

- **Decision:** custom templates are merged into the registry with `CUSTOM_BADGE` prefixed to their label; a broken TOML file or a name clash raises `TemplateError`, shown by the CLI as an error panel.
- **Why:** the menu picks up custom templates without touching `cli/`, which keeps lanes A and B on disjoint files; fail-fast matches the project's error-handling rules.
- **Given up:** the badge as pure presentation (it also appears in the metadata bar), and skipping a broken file with a warning while the rest keep working.

## 2026-10-14 — Lane B takes A1's contract by cherry-pick (pending approval)

- **Decision:** lane B cherry-picks lane A's contract commit `2f5a2b2` (`TemplateError`, `CUSTOM_BADGE`, `is_custom`) so `run_generate` can catch `TemplateError` and the branch's tests run; a preset source that fails to fetch aborts the flow (error panel) instead of falling back to the source prompt; the moved selection helpers lose their `_` prefix because `generate_cmd.py` now imports them from `cli/selections.py`.
- **Why:** lane rules forbid merging another lane's branch, and B3 cannot compile against `TemplateError` without it; the identical commit merges cleanly once the queue lands A before B. Aborting keeps `suggest` honest — the user picked that entry, a silent switch to a free-text prompt would be confusing.
- **Given up:** waiting for A to merge first (blocks the lane), a local stand-in exception class (two classes, one wrong), falling back to the prompt after a failed preset fetch.
