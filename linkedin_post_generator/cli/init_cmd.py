"""Init command — first-run configuration wizard."""

import os
import shutil

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from linkedin_post_generator.config import (
    AIBackend,
    AppConfig,
    Language,
    Length,
    Tone,
    save_config,
)

console = Console()


def _detect_ai_backend() -> AIBackend:
    """Auto-detect available AI backend."""
    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_claude_cli = shutil.which("claude") is not None

    if has_api_key:
        return AIBackend.API
    if has_claude_cli:
        return AIBackend.HEADLESS
    return AIBackend.AUTO


def _show_backend_status() -> AIBackend:
    """Show AI backend availability and return detected backend."""
    has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_claude_cli = shutil.which("claude") is not None

    if has_api_key:
        console.print("  [green]✓[/] ANTHROPIC_API_KEY ustawiony")
    else:
        console.print("  [dim]✗ ANTHROPIC_API_KEY nie ustawiony[/]")

    if has_claude_cli:
        console.print("  [green]✓[/] Claude CLI dostępne")
    else:
        console.print("  [dim]✗ Claude CLI niedostępne[/]")

    if not has_api_key and not has_claude_cli:
        console.print(
            "\n  [yellow]⚠️ Brak backendu AI.[/]"
            " Ustaw ANTHROPIC_API_KEY lub zainstaluj Claude CLI."
        )

    return _detect_ai_backend()


def init() -> None:
    """First-run configuration wizard."""
    console.print(
        Panel(
            "[cyan]Witaj w LinkedIn Post Generator![/]\n"
            "Skonfigurujmy podstawowe ustawienia.",
            title="🚀 Setup",
            border_style="cyan",
        )
    )

    # Language
    language = inquirer.select(
        message="Domyślny język postów:",
        choices=[
            {"name": "🇵🇱 Polski", "value": "pl"},
            {"name": "🇬🇧 English", "value": "en"},
        ],
        default="pl",
    ).execute()

    # Tone
    tone = inquirer.select(
        message="Domyślny ton:",
        choices=[
            {
                "name": "Professional-casual — ekspert, ale przystępny",
                "value": "professional-casual",
            },
            {
                "name": "Technical — precyzyjny, oparty na danych",
                "value": "technical",
            },
            {
                "name": "Storytelling — narracyjny, osobisty",
                "value": "storytelling",
            },
        ],
        default="professional-casual",
    ).execute()

    # Length
    length = inquirer.select(
        message="Domyślna długość:",
        choices=[
            {"name": "Short (500-800 znaków)", "value": "short"},
            {"name": "Standard (800-1300 znaków)", "value": "standard"},
            {"name": "Long (1300-2000 znaków)", "value": "long"},
        ],
        default="standard",
    ).execute()

    # Hashtags
    hashtags_input = inquirer.text(
        message="Domyślne hashtagi (oddzielone spacją, np. #Python #AI):",
        default="",
    ).execute()
    hashtags = hashtags_input.split() if hashtags_input.strip() else []

    # AI backend detection
    console.print("\n[cyan]Wykrywanie backendu AI...[/]")
    ai_backend = _show_backend_status()

    # Build config
    app_config = AppConfig(
        language=Language(language),
        tone=Tone(tone),
        length=Length(length),
        hashtags=hashtags,
        ai_backend=ai_backend,
    )

    # Save
    saved_path = save_config(app_config)

    # Summary
    table = Table(title="Konfiguracja", show_header=False, border_style="green")
    table.add_column("Pole", style="cyan")
    table.add_column("Wartość")
    table.add_row("Język", app_config.language.value)
    table.add_row("Ton", app_config.tone.value)
    table.add_row("Długość", app_config.length.value)
    table.add_row("Hashtagi", " ".join(hashtags) if hashtags else "(brak)")
    table.add_row("Backend AI", app_config.ai_backend.value)
    table.add_row("Zapisano w", str(saved_path))

    console.print()
    console.print(table)
    console.print("\n[green]✅ Konfiguracja zapisana. Możesz generować posty![/]")
