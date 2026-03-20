Mark the completed task in TODO.md and update related project files if needed.

This command is called automatically after `/start-work` finishes implementation.

## Step 1: Update TODO.md

1. Read `TODO.md`
2. Find the task that was just implemented
3. Change `- [ ]` to `- [x]` for the main task
4. Change `- [ ]` to `- [x]` for all completed sub-steps (if sub-steps use checkboxes)
5. Write the updated file

## Step 2: Check if CLAUDE.md needs updating

Read `CLAUDE.md` and check if the completed task changes anything documented there:
- New module/command added → update Architecture section
- New dependency added → update Tech Stack
- New CLI command → update Commands section
- Config format changed → update relevant section

If changes needed → apply them. If not → skip.

## Step 3: Check if per-directory CLAUDE.md files need updating

Check all `CLAUDE.md` files in directories that were affected by the completed task.
For each affected module directory (`linkedin_post_generator/cli/`, `linkedin_post_generator/fetcher/`, etc.):

- Public API changed (new functions, changed signatures) → update the module's CLAUDE.md
- Internal conventions changed → update
- New dependencies between modules → update
- File was created but directory has no CLAUDE.md yet → create one

If changes needed → apply them. If not → skip.

## Step 4: Check if README.md needs updating

Read `README.md` and check:
- New CLI command → update Commands table
- New feature → update Features list
- Config structure changed → update Configuration section

If changes needed → apply them. If not → skip.

## Step 4: Show summary

```
📝 Aktualizacja dokumentacji
- TODO.md: ✅ zadanie oznaczone jako wykonane
- CLAUDE.md (root): ✅ zaktualizowany / ⏭️ bez zmian
- CLAUDE.md (moduły): ✅ zaktualizowane (N plików) / ⏭️ bez zmian
- README.md: ✅ zaktualizowany / ⏭️ bez zmian
```

Show updated progress:
```
📊 Postęp MVP: X/Y zadań wykonanych (Z%)
```

## Step 5: Proceed to pre-commit

Execute `/pre-commit` to run quality checks before committing.

## Language

All output messages MUST be in Polish.
