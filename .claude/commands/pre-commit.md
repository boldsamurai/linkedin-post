Run a quality gate before committing. Check branch safety, code quality, tests, and working tree state.

## Step 1: Branch safety check

Run `git branch --show-current` to get the current branch name.

- If on `main` → "❌ Jesteś na głównym branchu `main`! Utwórz osobny branch przed commitem." and STOP.
- If on any other branch → proceed.

## Step 2: Ruff lint

Run `uv run ruff check .` and report results.
- If errors found → list them grouped by file, with line numbers
- If clean → "✅ Ruff lint: 0 błędów"

## Step 3: Ruff format

Run `uv run ruff format --check .` and report results.
- If formatting issues → list affected files
- If clean → "✅ Ruff format: ok"

If formatting issues found, use `AskUserQuestion`:
- "Napraw automatycznie" (description: "Uruchom `uv run ruff format .` i napraw formatowanie")
- "Pomiń" (description: "Kontynuuj bez naprawiania")

## Step 4: Tests

Run `uv run pytest --tb=short -q` and report results.
- If failures → show failed test names and short tracebacks
- If all pass → "✅ Testy: N passed"
- If no tests found → "⚠️ Brak testów"

## Step 5: Working tree check

Run `git status` and `git diff --cached --name-only` to inspect staged and unstaged files.

Flag potential problems:
- Staged files that shouldn't be committed (.env, credentials, __pycache__, .pyc, *.log)
- Untracked .py files that look like they should be committed (new files in linkedin_post_generator/ or tests/)
- Modified files that are NOT staged (remind user to stage or discard)

## Output format

### 🔍 Pre-commit check

| Krok | Status |
|------|--------|
| Branch | ✅ `<branch-name>` / ❌ main |
| Ruff lint | ✅ / ❌ (N błędów) |
| Ruff format | ✅ / ❌ (N plików) |
| Testy | ✅ (N passed) / ❌ (N failed) / ⚠️ brak |
| Git | ✅ / ⚠️ (szczegóły poniżej) |

If any step failed, show details below the table.

### Verdict

- If ALL green: proceed to ask about commit
- If any red: "❌ Popraw przed commitem:" + numbered list of issues to fix, then STOP
- If only warnings: "⚠️ Można commitować, ale sprawdź:" + list

### Commit prompt

If all checks pass (or only warnings), use `AskUserQuestion`:
- "Commituj" (description: "Przejdź do /commit — wygeneruj message i commituj")
- "Popraw najpierw" (description: "Chcę jeszcze coś poprawić przed commitem")
- "Pomiń commit" (description: "Zakończ bez commitowania")

If user selects "Commituj" → execute `/commit`.

## Language

All output messages MUST be in Polish.
