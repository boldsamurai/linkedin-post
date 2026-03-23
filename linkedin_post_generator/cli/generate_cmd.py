"""Generate command — interactive post generation flow."""

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from linkedin_post_generator.ai import AIError, generate
from linkedin_post_generator.cli.init_cmd import init as run_init
from linkedin_post_generator.config.model import Language, Length, Tone
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
from linkedin_post_generator.templates import build_prompt, get_template, list_templates

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
    if not config_exists():
        console.print("[cyan]Pierwsza konfiguracja — uruchamiam wizard...[/]\n")
        run_init()
        console.print()

    cfg = load_config()

    content = _source_input()
    if content is None:
        return

    # Dedup check
    _check_dedup(content.url)

    template_name = _select_template()
    language = _select_language(cfg.language)
    tone = _select_tone(cfg.tone)
    length = _select_length(cfg.length)

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


def _check_dedup(url: str) -> None:
    """Warn if this source URL was already used in history."""
    if not url:
        return
    try:
        store = get_store()
        existing = store.find_by_url(url)
        if existing:
            date = existing.created_at.strftime("%Y-%m-%d")
            console.print(
                f"[yellow]⚠️ Ten URL był już użyty {date} "
                f"(szablon: {existing.template})[/]"
            )
    except Exception:
        pass  # History DB issues shouldn't block generation


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
            return generate(
                prompt=user_message,
                system_prompt=system_prompt,
                backend=backend,
            )
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


def _source_input() -> FetchedContent | None:
    """Interactive source input step."""
    while True:
        user_input = Prompt.ask("\n[cyan]O czym chcesz napisać?[/] (URL lub temat)")

        if not user_input.strip():
            console.print("[yellow]Podaj URL lub temat.[/]")
            continue

        source_type = detect_source_type(user_input)

        try:
            content = _fetch_source(user_input.strip(), source_type)
        except FetchError as exc:
            _show_error(str(exc))
            continue

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

    body = f"[bold]{content.title}[/]\n\n[dim]{preview_text}[/]"
    if content.url:
        body += f"\n\n[underline blue]{content.url}[/]"

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


# --- Selection steps --------------------------------------------------------


def _select_template() -> str:
    """Interactive template selection with InquirerPy."""
    templates = list_templates()
    choices = [
        {"name": f"{t.label} — {t.description}", "value": t.name} for t in templates
    ]

    return inquirer.select(
        message="Szablon posta:",
        choices=choices,
        default=templates[0].name if templates else None,
    ).execute()


def _select_language(default: Language) -> Language:
    """Interactive language selection with config default pre-selected."""
    value = inquirer.select(
        message="Język posta:",
        choices=[
            {"name": "🇵🇱 Polski", "value": Language.PL.value},
            {"name": "🇬🇧 English", "value": Language.EN.value},
        ],
        default=default.value,
    ).execute()
    return Language(value)


def _select_tone(default: Tone) -> Tone:
    """Interactive tone selection with config default pre-selected."""
    value = inquirer.select(
        message="Ton posta:",
        choices=[
            {
                "name": "Professional-casual — ekspert, ale przystępny",
                "value": Tone.PROFESSIONAL_CASUAL.value,
            },
            {
                "name": "Technical — precyzyjny, oparty na danych",
                "value": Tone.TECHNICAL.value,
            },
            {
                "name": "Storytelling — narracyjny, osobisty",
                "value": Tone.STORYTELLING.value,
            },
        ],
        default=default.value,
    ).execute()
    return Tone(value)


def _select_length(default: Length) -> Length:
    """Interactive length selection with config default pre-selected."""
    value = inquirer.select(
        message="Długość posta:",
        choices=[
            {"name": "Short (500-800 znaków)", "value": Length.SHORT.value},
            {
                "name": "Standard (800-1300 znaków)",
                "value": Length.STANDARD.value,
            },
            {"name": "Long (1300-2000 znaków)", "value": Length.LONG.value},
        ],
        default=default.value,
    ).execute()
    return Length(value)
