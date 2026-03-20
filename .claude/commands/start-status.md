Run a status check at the start of a work session.

## Step 1: Remote sync

1. Run `git fetch origin` to update remote tracking info
2. Compare local vs remote for the current branch:
   - `git log HEAD..origin/<branch> --oneline` — commits on remote that you don't have locally
   - `git log origin/<branch>..HEAD --oneline` — local commits not pushed
3. If no remote tracking branch exists, report that

Report:
- "✅ Synchronizacja: lokalne repo aktualne" — if nothing to pull
- "⚠️ Remote ma N nowych commitów — rozważ `git pull`:" + list of commits
- "⚠️ Masz N lokalnych commitów niewypchniętych" — if local is ahead

## Step 2: Working tree

Run `git status` and report:
- Current branch name
- Uncommitted changes (staged and unstaged)
- Untracked files

If dirty: "⚠️ Masz niezacommitowane zmiany z poprzedniej sesji:" + file list

## Step 3: Stale branches

Run `git branch --list 'fix/*' 'feat/*' 'chore/*' 'refactor/*'` to find work branches.
For each, check if it was already merged into main: `git branch --merged main`

If found: "⚠️ Zmergowane branche do usunięcia:" + list

## Step 4: TODO.md Progress

Read `TODO.md` and report:
- Total number of tasks (lines with `[ ]` or `[x]`)
- How many are completed (`[x]`)
- How many remain (`[ ]`)
- What is the next uncompleted task (the first `[ ]` item)
- If TODO.md is empty or has no tasks, say so

## Step 5: Unfinished plans

Check if `.claude/plans/` contains any plan files.
If found, read each and report which have unchecked items (`- [ ]`):
- "⚠️ Niedokończony plan: `.claude/plans/feat-xyz.md` — 3/7 kroków wykonanych"

## Output format

### 🚀 Status sesji

| Krok | Status |
|------|--------|
| Remote sync | ✅ / ⚠️ (N commitów do pobrania) |
| Working tree | ✅ czyste / ⚠️ (N zmienionych plików) |
| Branch | `<current-branch>` |
| Stale branches | ✅ brak / ⚠️ (N do usunięcia) |
| TODO | ✅ X/Y zadań wykonanych / ⚠️ brak zadań |
| Niedokończone plany | ✅ brak / ⚠️ (N planów) |

If any warnings, show details below the table.

### Verdict

- If ALL green: "✅ Gotowe do pracy"
- If warnings: list recommended actions with exact commands to run

## Language

All output messages MUST be in Polish.
