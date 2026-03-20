Display the project workflow — the full development pipeline with available commands.

Show the following output exactly (do NOT modify the diagram or descriptions):

```
WORKFLOW -- LinkedIn Post Generator

+------------------------------------------------------+
|                     START SESJI                       |
|                                                      |
| /start-status    Stan projektu, git, TODO, plany     |
|        |                                             |
|        v                                             |
| /next-task       Nastepne zadanie + kontekst         |
|        |                                             |
|        v                                             |
| /start-work      Plan, akceptacja, kodowanie, testy  |
|        |                                             |
|        v                                             |
| /update-todo     Oznacz task, aktualizuj docs        |
|        |                                             |
|        v                                             |
| /pre-commit      Ruff + testy + git (quality gate)   |
|        |                                             |
|        v                                             |
| /commit          Conventional commit + push          |
|                                                      |
+------------------------------------------------------+
```

## Automatyczne przejścia

Pipeline jest połączony — każda komenda uruchamia następną:
- `/next-task` → "Zaczynamy" → automatycznie `/start-work`
- `/start-work` → po implementacji → automatycznie `/update-todo`
- `/update-todo` → po aktualizacji → automatycznie `/pre-commit`
- `/pre-commit` → "Commituj" → automatycznie `/commit`

Wystarczy odpalić `/next-task` i pipeline prowadzi do końca.

## Skróty — komendy samodzielne

Każdą komendę można odpalić niezależnie:

| Komenda | Kiedy użyć samodzielnie |
|---------|------------------------|
| `/start-status` | Na początku sesji — sprawdź stan projektu |
| `/next-task` | Szukasz co robić dalej |
| `/start-work` | Chcesz ręcznie wskazać zadanie do implementacji |
| `/update-todo` | Ręcznie oznaczasz task jako zrobiony |
| `/pre-commit` | Sprawdzasz jakość kodu bez commitowania |
| `/commit` | Commitujesz zmiany bez pełnego pipeline'u |
| `/workflow` | Przypomnienie tego schematu |

## Language

All output messages MUST be in Polish.
