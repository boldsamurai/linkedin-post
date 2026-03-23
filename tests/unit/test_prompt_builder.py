"""Tests for prompt assembly — system prompts and user messages."""

from linkedin_post_generator.ai.prompt_builder import (
    LANGUAGE_INSTRUCTIONS,
    LENGTH_RANGES,
    SYSTEM_PROMPT_BASE,
    TONE_INSTRUCTIONS,
    build_system_prompt,
    build_user_message,
)
from linkedin_post_generator.config.model import Language, Length, Tone


class TestBuildSystemPrompt:
    """System prompt assembly from components."""

    def test_contains_base_role(self) -> None:
        result = build_system_prompt(
            template_instructions="Test template",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert SYSTEM_PROMPT_BASE in result

    def test_contains_template_instructions(self) -> None:
        result = build_system_prompt(
            template_instructions="Focus on discovery and sharing tools",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert "Focus on discovery and sharing tools" in result

    def test_contains_language_instruction_polish(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.PL,
            length=Length.STANDARD,
        )
        assert LANGUAGE_INSTRUCTIONS[Language.PL] in result

    def test_contains_language_instruction_english(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert LANGUAGE_INSTRUCTIONS[Language.EN] in result

    def test_contains_tone_professional_casual(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert TONE_INSTRUCTIONS[Tone.PROFESSIONAL_CASUAL] in result

    def test_contains_tone_technical(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.TECHNICAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert TONE_INSTRUCTIONS[Tone.TECHNICAL] in result

    def test_contains_tone_storytelling(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.STORYTELLING,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert TONE_INSTRUCTIONS[Tone.STORYTELLING] in result

    def test_contains_length_range_short(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.SHORT,
        )
        assert "500-800 characters" in result

    def test_contains_length_range_standard(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert "800-1300 characters" in result

    def test_contains_length_range_long(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.LONG,
        )
        assert "1300-2000 characters" in result

    def test_contains_anti_patterns(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert "NEVER use these patterns" in result

    def test_contains_emoji_policy(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert "max 2-4 emoji" in result.lower() or "Max 2-4 emoji" in result

    def test_contains_output_format(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
        )
        assert "plain text only" in result

    def test_includes_hashtags_when_provided(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
            hashtags=["#Python", "#DevOps"],
        )
        assert "#Python" in result
        assert "#DevOps" in result
        assert "Always include these hashtags" in result

    def test_no_include_line_when_no_hashtags(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
            hashtags=[],
        )
        assert "Always include these hashtags" not in result

    def test_no_include_line_when_hashtags_none(self) -> None:
        result = build_system_prompt(
            template_instructions="Test",
            tone=Tone.PROFESSIONAL_CASUAL,
            language=Language.EN,
            length=Length.STANDARD,
            hashtags=None,
        )
        assert "Always include these hashtags" not in result

    def test_all_tones_have_instructions(self) -> None:
        for tone in Tone:
            assert tone in TONE_INSTRUCTIONS, f"Missing instructions for {tone}"

    def test_all_lengths_have_ranges(self) -> None:
        for length in Length:
            assert length in LENGTH_RANGES, f"Missing range for {length}"

    def test_all_languages_have_instructions(self) -> None:
        for lang in Language:
            assert lang in LANGUAGE_INSTRUCTIONS, f"Missing instruction for {lang}"


class TestBuildUserMessage:
    """User message wraps source content."""

    def test_contains_source_content(self) -> None:
        result = build_user_message("Python decorators are awesome!")
        assert "Python decorators are awesome!" in result

    def test_has_instruction_prefix(self) -> None:
        result = build_user_message("some content")
        assert "Write a LinkedIn post" in result

    def test_wraps_with_separators(self) -> None:
        result = build_user_message("content here")
        assert "---" in result
