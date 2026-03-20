Find the next uncompleted task from TODO.md and present it with full context.

## Step 1: Read TODO.md

Read `TODO.md` and find the first unchecked task (`- [ ]`) in the **MVP** section.
If all MVP tasks are done, look in **Post-MVP**.
If everything is done → "✅ Wszystkie zadania wykonane!"

## Step 2: Show task context

Display the task with its sub-steps in a Rich-style block:

```
📋 Następne zadanie
Sekcja: [section name, e.g. "Config System"]
Zadanie: [task description]

Podzadania:
  - [sub-step 1]
  - [sub-step 2]
  - ...
```

## Step 3: Show progress

Read all tasks from TODO.md and show progress:

```
📊 Postęp: X/Y zadań MVP wykonanych (Z%)
```

## Step 4: Check prerequisites

Before starting, verify:
- Are there any tasks from earlier sections that are still unchecked? If yes → "⚠️ Wcześniejsze zadanie niezakończone: [task]. Rozważ dokończenie najpierw."
- Are there uncommitted changes in git? If yes → "⚠️ Masz niezacommitowane zmiany z poprzedniej sesji."

## Step 5: Ask to start

Use `AskUserQuestion` with the question "Co robimy?" and options:
- "Zaczynamy" (description: "Przejdź do planowania i implementacji tego zadania — uruchomi /start-work")
- "Pokaż inne zadanie" (description: "Chcę zobaczyć inne zadanie z listy — powiem które")
- "Nie teraz" (description: "Wróć do wolnej pracy")

If user selects "Zaczynamy" → execute `/start-work` for this task.

## Language

All output messages MUST be in Polish.
