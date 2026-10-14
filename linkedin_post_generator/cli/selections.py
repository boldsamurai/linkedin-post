"""Interactive selection steps: template, language, tone, length."""

from InquirerPy import inquirer
from rich.console import Console

from linkedin_post_generator.config.model import AppConfig, Language, Length, Tone
from linkedin_post_generator.templates import list_templates

console = Console()

_LANG_LABELS = {Language.PL: "🇵🇱 Polski", Language.EN: "🇬🇧 English"}
_TONE_LABELS = {
    Tone.PROFESSIONAL_CASUAL: "Professional-casual",
    Tone.TECHNICAL: "Technical",
    Tone.STORYTELLING: "Storytelling",
}
_LENGTH_LABELS = {
    Length.SHORT: "Short (500-800)",
    Length.STANDARD: "Standard (800-1300)",
    Length.LONG: "Long (1300-2000)",
}


def confirm_or_change_defaults(
    cfg: AppConfig,
) -> tuple[Language, Tone, Length]:
    """Show config defaults and let user confirm or change them.

    Returns:
        Tuple of (language, tone, length).
    """
    language = cfg.language
    tone = cfg.tone
    length = cfg.length

    console.print(
        f"\n  [dim]Ustawienia:[/] {_LANG_LABELS[language]} | "
        f"{_TONE_LABELS[tone]} | {_LENGTH_LABELS[length]}"
    )

    change = inquirer.select(
        message="Zmienić ustawienia?",
        choices=[
            {"name": "Nie, generuj →", "value": False},
            {"name": "Tak, zmień", "value": True},
        ],
        default=False,
    ).execute()

    if change:
        language = select_language(language)
        tone = select_tone(tone)
        length = select_length(length)

    return language, tone, length


def select_template() -> str:
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


def select_language(default: Language) -> Language:
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


def select_tone(default: Tone) -> Tone:
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


def select_length(default: Length) -> Length:
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
