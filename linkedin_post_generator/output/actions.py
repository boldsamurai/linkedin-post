"""Post-generation action menu — copy, save, exit loop."""

from InquirerPy import inquirer

from linkedin_post_generator.output.clipboard import copy_to_clipboard
from linkedin_post_generator.output.file_save import save_to_file

ACTION_COPY = "copy"
ACTION_SAVE = "save"
ACTION_REFINE = "refine"
ACTION_NEW = "new"
ACTION_EXIT = "exit"


def post_action_menu(
    post_text: str,
    source_title: str,
    template_name: str,
    language: str,
) -> str:
    """Interactive action menu after post generation.

    Loops until user selects Exit or Refine (which returns control
    to the caller for re-generation).

    Args:
        post_text: The generated post text.
        source_title: Title of the source material.
        template_name: Template used.
        language: Language code.

    Returns:
        The last selected action (ACTION_REFINE, ACTION_NEW, or ACTION_EXIT).
    """
    while True:
        action = inquirer.select(
            message="Co dalej?",
            choices=[
                {"name": "📋 Kopiuj do schowka", "value": ACTION_COPY},
                {"name": "💾 Zapisz do pliku", "value": ACTION_SAVE},
                {"name": "✏️  Popraw ten draft", "value": ACTION_REFINE},
                {"name": "🔄 Generuj nową wersję", "value": ACTION_NEW},
                {"name": "👋 Zakończ", "value": ACTION_EXIT},
            ],
        ).execute()

        if action == ACTION_COPY:
            copy_to_clipboard(post_text)
            continue

        if action == ACTION_SAVE:
            save_to_file(
                text=post_text,
                source_title=source_title,
                template_name=template_name,
                language=language,
            )
            continue

        # Refine, New, or Exit — return to caller
        return action
