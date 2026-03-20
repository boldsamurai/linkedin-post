Plan and implement the current task from TODO.md.

This command is called after `/next-task` selects a task, or can be called directly with a task description.

## Step 1: Gather context

1. Read `TODO.md` — identify the current task and its sub-steps
2. Read `CLAUDE.md` — understand project architecture and conventions
3. Read relevant source files that will be affected by this task
4. Check `git status` — verify clean working tree (warn if dirty)

## Step 2: Create implementation plan

Based on the task and its sub-steps, create a detailed plan:

```
🔧 Plan implementacji: [task name]

1. [concrete step — which file to create/modify, what to add]
2. [concrete step]
3. ...
N. Testy: [what tests to write]
```

The plan must:
- Map each sub-step from TODO.md to a concrete code action
- Specify which files will be created or modified
- Include test steps at the end
- Be ordered by dependency (create base modules before modules that import them)

## Step 3: Ask for approval

Use `AskUserQuestion` with the question "Plan wygląda ok?" and options:
- "Tak, implementuj" (description: "Rozpocznij implementację według planu")
- "Zmień plan" (description: "Chcę zmodyfikować plan — powiem co zmienić")
- "Anuluj" (description: "Wróć bez implementacji")

## Step 4: Implement

If approved, execute the plan step by step:
- Create/modify files as planned
- **When creating a new directory:** also create a `CLAUDE.md` in it describing the module's responsibility, public API, and internal conventions (see root CLAUDE.md "Per-Directory CLAUDE.md" section)
- After each logical chunk of work, briefly report what was done
- Write tests as specified in the plan
- Run `uv run ruff check .` and `uv run ruff format .` after writing code
- Run `uv run pytest` after writing tests

## Step 5: Verify

After implementation is complete:
1. Run `uv run ruff check .` — fix any issues
2. Run `uv run pytest` — all tests must pass
3. Run `git diff --stat` — show what files changed

## Step 6: Finish

Display summary:

```
✅ Implementacja zakończona: [task name]
- Utworzone pliki: [list]
- Zmodyfikowane pliki: [list]
- Testy: N passed
```

Then execute `/update-todo` to mark the task as complete.

## Language

All output messages MUST be in Polish.
