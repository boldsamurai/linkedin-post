# Project Memory

> Living document — architecture decisions, known issues, recent changes.
> Updated at decision time (not review time). Reviewed bi-weekly.
>
> See `.claude/rules/memory.md` for what goes here vs CLAUDE.md vs auto-memory.

## Architecture

<!--
High-level system overview. Database, auth mechanism, service boundaries, key tech choices.
Include rationale where non-obvious. Keep concise — Claude already infers structure from code.

Example:
- API: FastAPI with async SQLAlchemy + asyncpg
- Auth: JWT in httpOnly cookies, refreshed every 15 min
- Storage adapter pattern (StorageBackend abstract) — chose over direct boto3 calls so we can swap S3 ↔ local without touching call sites
-->

## Key Design Decisions

<!--
Format: [YYYY-MM-DD] decision — rationale (and trade-off accepted)

Add ENTRIES at the time of decision. Don't backfill from memory weeks later.

Example:
- [2026-04-10] storage adapter pattern with thumbnails — needed swap-able backend for tests; trade-off: extra abstraction layer
- [2026-04-15] Przelewy24 over Stripe — Polish bank transfers, lower fees for PL market; trade-off: less mature SDK
-->

## Known Issues (Do Not Fix)

<!--
Intentional oddities Claude shouldn't "fix" without asking. Include WHY they exist.

Example:
- `# type: ignore` on line 47 of app/auth/jwt.py — pyjwt 2.x type stubs are wrong, fix is pending upstream
- Hardcoded retry=3 in payments/p24.py — required by Przelewy24 spec, not configurable
-->

## Recently Changed (30-day window)

<!--
Major changes in the last month. Helps Claude understand current state without reading whole git log.
Prune entries >30 days at next review.

Format: [YYYY-MM-DD] what changed — affected modules

Example:
- [2026-04-10] migrated photo upload to S3 backend — app/storage/, tests/integration/
- [2026-04-05] added thumbnail generation — app/storage/thumbnail.py, requires Pillow
-->

## Active Work

<!--
What's currently in progress and blocking. Updated more frequently than other sections.

Example:
- PR #42 (Przelewy24 integration) — waiting for sandbox credentials from finance team
- Task "implement webhook signature validation" — blocked on getting Przelewy24 docs
-->
