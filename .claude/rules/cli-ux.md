---
globs: ["linkedin_post_generator/cli/**", "linkedin_post_generator/output/**"]
---

# CLI UX Rules

## Interactive menus — InquirerPy
- Use `InquirerPy` for all selection menus (template, language, tone, length, action menu)
- Arrow keys (↑↓) + Enter to select
- Every option shows: short label + one-line description
- Config defaults shown as pre-selected option
- Always provide a "Back" or "Cancel" option

## Rich theme — green accent
- Success / post panel: `green`
- Warnings: `yellow`
- Errors: `red bold`
- Info / labels: `cyan`
- Post content inside panel: `white` on default background (readability first)
- Hashtags in posts: `blue`
- URLs in posts: `underline blue`

## Post display — Rich Panel
- Generated post: `rich.panel.Panel` with border style `green`, title "📝 Draft"
- Post text inside panel: plain white, no syntax highlighting (this is how it will look on LinkedIn)
- Metadata bar below panel: `template | language | character count | word count`
- Example:
  ```
  ┌─────────── 📝 Draft ───────────┐
  │                                 │
  │  [post content here]            │
  │                                 │
  └─────────────────────────────────┘
    Discovery | EN | 847 chars | 142 words
  ```

## Spinners — Rich Status
- AI generation: `rich.status.Status` with "🤖 Generowanie posta..."
- URL fetching: "🔗 Pobieranie treści..."
- GitHub API: "🔗 Pobieranie danych z GitHub..."
- Always show what's happening — never a silent wait

## Error display — Rich Panel with instructions
- All errors: red `rich.panel.Panel` with title "❌ Error"
- Panel body: short error message + concrete instruction what to do
- Examples:
  - AI timeout → "Przekroczono czas oczekiwania. Spróbuj ponownie."
  - No internet → "Nie udało się połączyć. Sprawdź połączenie z internetem."
  - Bad URL → "Nie udało się pobrać treści z podanego URL. Sprawdź czy link jest poprawny."
  - No AI backend → "Nie znaleziono Claude Code CLI ani ANTHROPIC_API_KEY. Uruchom `linkedin-post init` aby skonfigurować."
- Never show raw stack traces — log them internally, show friendly message

## Tables — history
- `rich.table.Table` with columns: ID, Date, Source (truncated), Template, Language
- Max 20 rows per page, most recent first
- Truncate long values with `...` (max 50 chars for source column)

## Messages — consistent patterns
- Success: "✅ [action completed]" (e.g., "✅ Post skopiowany do schowka")
- Warning: "⚠️ [what happened]" (e.g., "⚠️ Ten URL był już użyty 2025-12-01")
- Action prompts: direct question, no filler ("Co dalej?" not "Co chciałbyś teraz zrobić?")
- Confirmations: state what will happen ("Usunąć post #12?" not "Czy na pewno?")

## Action menu pattern
- Used after post generation and in history management
- InquirerPy select menu with options
- After generation: Copy to clipboard / Save to file / Refine / Generate new version / Exit
- After action (except Exit): return to menu — loop until user exits

## First-run experience
- No config found → friendly welcome + auto-start init wizard
- No errors about missing config — guide the user
- After init: "✅ Konfiguracja zapisana. Możesz generować posty!"
