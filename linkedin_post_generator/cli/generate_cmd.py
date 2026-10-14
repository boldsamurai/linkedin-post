"""Generate command — interactive post generation flow."""

from InquirerPy import inquirer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt

from linkedin_post_generator.ai import AIError, generate
from linkedin_post_generator.ai.cleaner import clean_ai_response
from linkedin_post_generator.cli.init_cmd import init as run_init
from linkedin_post_generator.cli.selections import (
    confirm_or_change_defaults,
    select_template,
)
from linkedin_post_generator.config.reader import config_exists, load_config
from linkedin_post_generator.fetcher import (
    FetchedContent,
    FetchError,
    create_note,
    detect_source_type,
    fetch_github_repo,
    fetch_url,
    prompt_for_note,
)
from linkedin_post_generator.fetcher.models import SourceType
from linkedin_post_generator.history import get_store
from linkedin_post_generator.output import (
    ACTION_EXIT,
    ACTION_NEW,
    ACTION_REFINE,
    display_post,
    post_action_menu,
)
from linkedin_post_generator.templates import TemplateError, build_prompt, get_template

console = Console()

_SOURCE_TYPE_LABELS: dict[SourceType, str] = {
    SourceType.GITHUB: "GitHub",
    SourceType.URL: "URL",
    SourceType.TEXT: "Notatka",
}

_SPINNER_MESSAGES: dict[SourceType, str] = {
    SourceType.GITHUB: "🔗 Pobieranie danych z GitHub...",
    SourceType.URL: "🔗 Pobieranie treści...",
}


def generate_cmd() -> None:
    """Interactive post generation flow."""
    run_generate()


def run_generate(source_input: str | None = None) -> None:
    """Run the generate flow, optionally starting from a preset source.

    Args:
        source_input: URL or topic to use instead of prompting for one.
            Fetch, preview and dedup check still run for it.
    """
    try:
        _generate_flow(source_input)
    except TemplateError as exc:
        _show_template_error(exc)


def _generate_flow(source_input: str | None) -> None:
    """Source → template → settings → generation → action loop."""
    if not config_exists():
        console.print("[cyan]Pierwsza konfiguracja — uruchamiam wizard...[/]\n")
        run_init()
        console.print()

    cfg = load_config()

    content = _source_input(source_input)
    if content is None:
        return

    # Dedup check
    if not _check_dedup(content.url):
        return

    template_name = select_template()
    language, tone, length = confirm_or_change_defaults(cfg)

    template = get_template(template_name)
    system_prompt, user_message = build_prompt(
        template_name=template_name,
        source_content=content.text,
        tone=tone,
        language=language,
        length=length,
        hashtags=cfg.hashtags,
    )

    # --- Generate + action loop ---
    post_text = _generate_post(system_prompt, user_message, cfg.ai_backend)
    if post_text is None:
        return

    # Auto-save to history
    _save_to_history(content, template_name, language.value, tone.value, post_text)

    while True:
        display_post(
            text=post_text,
            template_label=template.label,
            language=language.value,
        )

        action = post_action_menu(
            post_text=post_text,
            source_title=content.title,
            template_name=template_name,
            language=language.value,
        )

        if action == ACTION_EXIT:
            return

        if action == ACTION_REFINE:
            feedback = _ask_refinement_feedback()
            if not feedback:
                continue
            user_message = _build_refinement_prompt(post_text, feedback)
            post_text = _generate_post(system_prompt, user_message, cfg.ai_backend)
            if post_text is None:
                return
            continue

        if action == ACTION_NEW:
            # Re-generate with same params, fresh prompt
            _, user_message = build_prompt(
                template_name=template_name,
                source_content=content.text,
                tone=tone,
                language=language,
                length=length,
                hashtags=cfg.hashtags,
            )
            post_text = _generate_post(system_prompt, user_message, cfg.ai_backend)
            if post_text is None:
                return
            continue


# --- History ----------------------------------------------------------------


def _check_dedup(url: str) -> bool:
    """Check if source URL was already used. Returns False to abort.

    Returns:
        True to continue, False to abort generation.
    """
    if not url:
        return True
    try:
        store = get_store()
        existing = store.find_by_url(url)
        if not existing:
            return True

        date = existing.created_at.strftime("%Y-%m-%d")
        console.print(
            f"\n[yellow]⚠️ Ten URL był już użyty {date} "
            f"(szablon: {existing.template})[/]"
        )

        action = inquirer.select(
            message="Co robimy?",
            choices=[
                {"name": "Kontynuuj mimo to", "value": "continue"},
                {
                    "name": "Pokaż istniejący post",
                    "value": "show",
                },
                {"name": "Anuluj", "value": "cancel"},
            ],
        ).execute()

        if action == "cancel":
            return False

        if action == "show":
            from linkedin_post_generator.output import display_post

            display_post(
                text=existing.post_text,
                template_label=existing.template,
                language=existing.language,
            )
            # After showing, ask again
            proceed = inquirer.select(
                message="Generować nowy post z tego samego URL?",
                choices=[
                    {"name": "Tak, generuj nowy", "value": "continue"},
                    {"name": "Nie, anuluj", "value": "cancel"},
                ],
            ).execute()
            return proceed == "continue"

        return True  # "continue"
    except Exception:
        return True  # DB issues shouldn't block


def _save_to_history(
    content: FetchedContent,
    template_name: str,
    language: str,
    tone: str,
    post_text: str,
) -> None:
    """Auto-save generated post to history."""
    try:
        store = get_store()
        store.save(
            source_type=("url" if content.url else "text"),
            source_url=content.url,
            source_text=content.text,
            template=template_name,
            language=language,
            tone=tone,
            post_text=post_text,
        )
    except Exception:
        pass  # History DB issues shouldn't block generation


# --- AI generation ----------------------------------------------------------


def _generate_post(
    system_prompt: str,
    user_message: str,
    backend: str,
) -> str | None:
    """Generate post text via AI backend with spinner and error handling.

    Returns:
        Generated post text, or None if generation failed.
    """
    try:
        with console.status("🤖 Generowanie posta..."):
            raw = generate(
                prompt=user_message,
                system_prompt=system_prompt,
                backend=backend,
            )
        return clean_ai_response(raw)
    except AIError as exc:
        console.print(
            Panel(
                f"{exc}\n\n[dim]Sprawdź konfigurację AI "
                "(`linkedin-post init`) i spróbuj ponownie.[/]",
                title="❌ Błąd generowania",
                border_style="red bold",
            )
        )
        return None


# --- Refinement -------------------------------------------------------------


def _ask_refinement_feedback() -> str:
    """Prompt user for refinement feedback.

    Returns:
        Feedback text, or empty string if cancelled.
    """
    return Prompt.ask("\n[cyan]Co zmienić?[/]").strip()


def _build_refinement_prompt(original_post: str, feedback: str) -> str:
    """Build a refinement prompt with original post and feedback.

    Args:
        original_post: The current version of the post.
        feedback: User's refinement instructions.

    Returns:
        New user message incorporating original + feedback.
    """
    return (
        "Here is the current version of the LinkedIn post:\n\n"
        f"---\n{original_post}\n---\n\n"
        "Modify the existing post based on this feedback. "
        "Keep everything else unchanged unless the feedback "
        "implies otherwise.\n\n"
        f"Feedback: {feedback}"
    )


# --- Source input -----------------------------------------------------------


def _source_input(preset: str | None = None) -> FetchedContent | None:
    """Interactive source input step.

    Args:
        preset: Source chosen elsewhere (e.g. by ``suggest``); skips the prompt.

    Returns:
        Fetched content, or None when a preset source cannot be fetched.
    """
    if preset is not None:
        return _fetch_and_preview(preset.strip())

    while True:
        user_input = Prompt.ask("\n[cyan]O czym chcesz napisać?[/] (URL lub temat)")

        if not user_input.strip():
            console.print("[yellow]Podaj URL lub temat.[/]")
            continue

        content = _fetch_and_preview(user_input.strip())
        if content is not None:
            return content


def _fetch_and_preview(user_input: str) -> FetchedContent | None:
    """Fetch a source and show its preview; None when the fetch failed."""
    source_type = detect_source_type(user_input)

    try:
        content = _fetch_source(user_input, source_type)
    except FetchError as exc:
        _show_error(str(exc))
        return None

    _show_source_preview(content, source_type)
    return content


def _fetch_source(user_input: str, source_type: SourceType) -> FetchedContent:
    """Fetch content based on detected source type."""
    if source_type == SourceType.GITHUB:
        with console.status(_SPINNER_MESSAGES[SourceType.GITHUB]):
            return fetch_github_repo(user_input)

    if source_type == SourceType.URL:
        with console.status(_SPINNER_MESSAGES[SourceType.URL]):
            return fetch_url(user_input)

    if len(user_input) < 20:
        console.print(f"\n📝 Temat: [bold]{user_input}[/]")
        return prompt_for_note()

    return create_note(user_input)


def _show_source_preview(content: FetchedContent, source_type: SourceType) -> None:
    """Show a preview of fetched source content."""
    label = _SOURCE_TYPE_LABELS.get(source_type, "Źródło")

    preview_text = content.text[:200]
    if len(content.text) > 200:
        preview_text += "..."

    # Titles and text come from remote pages; never let them act as Rich markup.
    body = f"[bold]{escape(content.title)}[/]\n\n[dim]{escape(preview_text)}[/]"
    if content.url:
        body += f"\n\n[underline blue]{escape(content.url)}[/]"

    console.print(Panel(body, title=f"📄 {label}", border_style="cyan"))


def _show_error(message: str) -> None:
    """Show a fetch error with retry instruction."""
    console.print(
        Panel(
            f"{message}\n\n[dim]Spróbuj ponownie z innym URL lub wpisz temat.[/]",
            title="❌ Error",
            border_style="red bold",
        )
    )


def _show_template_error(exc: TemplateError) -> None:
    """Show a broken custom template file with a fix instruction."""
    console.print(
        Panel(
            f"Nieprawidłowy plik szablonu: {escape(str(exc.path))}\n"
            f"{escape(exc.reason)}\n\n"
            "[dim]Popraw lub usuń ten plik i uruchom polecenie ponownie.[/]",
            title="❌ Error",
            border_style="red bold",
        )
    )
