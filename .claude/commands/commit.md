Commit current changes with an auto-generated conventional commit message.

## Step 1: Check state

Run `git status` and `git diff --stat`.

If no changes → "Brak zmian do commitowania." and STOP.

## Step 2: Generate commit message

Based on `git diff --stat` and `git diff`, generate a commit message in conventional commits format:

```
<type>(<scope>): <description>

<body — optional, max 3 lines>
```

Types:
- `feat` — new feature
- `fix` — bug fix
- `refactor` — refactoring without behavior change
- `test` — adding/changing tests
- `docs` — documentation
- `chore` — configuration, tooling, dependencies

Scope = module name (cli, config, fetcher, ai, templates, history, output, tests).

Examples:
- `feat(cli): implement interactive generate flow`
- `feat(config): add TOML config reader with XDG paths`
- `test(history): add SQLite CRUD tests`
- `chore: update pyproject.toml dependencies`
- `docs: update README with interactive CLI flow`

Rules:
- Subject line max 72 chars
- English only
- Focus on "why" not "what"
- Never include `Co-Authored-By` in the message

## Step 3: Show preview

Display commit message and file list in a code block, then use `AskUserQuestion`:
- "Zatwierdź i push" (description: "Commituj zmiany i wypchnij do remote")
- "Zatwierdź bez push" (description: "Commituj, ale nie pushuj")
- "Edytuj message" (description: "Chcę zmienić treść commit message")
- "Anuluj" (description: "Nie commituj, wróć do pracy")

## Step 4: Execute

If approved:
1. `git add -A`
2. `git commit -m "<message>"`
3. If "Zatwierdź i push": `git push` (if push fails — show command and continue)
4. Show: "✅ Commit: `<short-hash>` — `<subject line>`"

If "Edytuj message":
1. Ask user for the new message
2. Show preview again
3. Return to Step 3

## Language

All output messages MUST be in Polish.
