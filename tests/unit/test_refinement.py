"""Tests for iterative refinement — prompt building and generation."""

from unittest.mock import MagicMock, patch

from linkedin_post_generator.cli.generate_cmd import (
    _build_refinement_prompt,
    _generate_post,
)


class TestBuildRefinementPrompt:
    """Refinement prompt includes original post and feedback."""

    def test_contains_original_post(self) -> None:
        result = _build_refinement_prompt(
            original_post="My LinkedIn post about Python.",
            feedback="Make it shorter",
        )
        assert "My LinkedIn post about Python." in result

    def test_contains_feedback(self) -> None:
        result = _build_refinement_prompt(
            original_post="Some post",
            feedback="Add more emoji",
        )
        assert "Add more emoji" in result

    def test_contains_modification_instruction(self) -> None:
        result = _build_refinement_prompt(
            original_post="Post",
            feedback="less formal",
        )
        assert "Modify the existing post" in result

    def test_contains_keep_unchanged_instruction(self) -> None:
        result = _build_refinement_prompt(
            original_post="Post",
            feedback="feedback",
        )
        assert "Keep everything else unchanged" in result


class TestGeneratePost:
    """AI generation wrapper with error handling."""

    @patch("linkedin_post_generator.cli.generate_cmd.generate")
    def test_returns_generated_text(self, mock_gen: MagicMock) -> None:
        mock_gen.return_value = "Generated post text"
        result = _generate_post("system", "user msg", "auto")
        assert result == "Generated post text"

    @patch("linkedin_post_generator.cli.generate_cmd.generate")
    def test_passes_correct_args(self, mock_gen: MagicMock) -> None:
        mock_gen.return_value = "text"
        _generate_post("sys prompt", "user msg", "api")
        mock_gen.assert_called_once_with(
            prompt="user msg",
            system_prompt="sys prompt",
            backend="api",
        )

    @patch("linkedin_post_generator.cli.generate_cmd.generate")
    def test_returns_none_on_error(self, mock_gen: MagicMock) -> None:
        from linkedin_post_generator.ai.exceptions import AINotAvailableError

        mock_gen.side_effect = AINotAvailableError("No backend")
        result = _generate_post("system", "user msg", "auto")
        assert result is None
