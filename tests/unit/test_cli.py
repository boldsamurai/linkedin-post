"""Tests for CLI commands — smoke tests, init wizard, auto-init."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from linkedin_post_generator.cli import app

runner = CliRunner()


class TestCLISmoke:
    """Smoke tests — --help works for all commands."""

    def test_main_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "linkedin-post" in result.output.lower() or "Usage" in result.output

    def test_version(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_init_help(self):
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "wizard" in result.output.lower()

    def test_generate_help(self):
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0

    def test_config_help(self):
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0

    def test_history_help(self):
        result = runner.invoke(app, ["history", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "show" in result.output
        assert "search" in result.output
        assert "delete" in result.output

    def test_history_list_help(self):
        result = runner.invoke(app, ["history", "list", "--help"])
        assert result.exit_code == 0

    def test_history_show_help(self):
        result = runner.invoke(app, ["history", "show", "--help"])
        assert result.exit_code == 0

    def test_history_search_help(self):
        result = runner.invoke(app, ["history", "search", "--help"])
        assert result.exit_code == 0

    def test_history_delete_help(self):
        result = runner.invoke(app, ["history", "delete", "--help"])
        assert result.exit_code == 0


class TestInitCommand:
    """Tests for the init wizard."""

    @patch("linkedin_post_generator.cli.init_cmd.inquirer")
    @patch("linkedin_post_generator.cli.init_cmd.save_config")
    def test_init_saves_config(self, mock_save, mock_inquirer, tmp_path):
        mock_select = MagicMock()
        mock_text = MagicMock()

        mock_select.execute = MagicMock(
            side_effect=["pl", "professional-casual", "standard"]
        )
        mock_text.execute = MagicMock(return_value="#Python #AI")

        mock_inquirer.select = MagicMock(return_value=mock_select)
        mock_inquirer.text = MagicMock(return_value=mock_text)

        mock_save.return_value = tmp_path / "config.toml"

        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert mock_save.called

        saved_config = mock_save.call_args[0][0]
        assert saved_config.language.value == "pl"
        assert saved_config.tone.value == "professional-casual"
        assert saved_config.hashtags == ["#Python", "#AI"]

    @patch("linkedin_post_generator.cli.init_cmd.inquirer")
    @patch("linkedin_post_generator.cli.init_cmd.save_config")
    def test_init_empty_hashtags(self, mock_save, mock_inquirer, tmp_path):
        mock_select = MagicMock()
        mock_text = MagicMock()

        mock_select.execute = MagicMock(side_effect=["en", "technical", "long"])
        mock_text.execute = MagicMock(return_value="")

        mock_inquirer.select = MagicMock(return_value=mock_select)
        mock_inquirer.text = MagicMock(return_value=mock_text)

        mock_save.return_value = tmp_path / "config.toml"

        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        saved_config = mock_save.call_args[0][0]
        assert saved_config.language.value == "en"
        assert saved_config.hashtags == []


class TestAutoInit:
    """Tests for auto-init on generate."""

    @patch("linkedin_post_generator.cli.generate_cmd._source_input", return_value=None)
    @patch("linkedin_post_generator.cli.generate_cmd.config_exists")
    def test_generate_skips_init_when_config_exists(
        self, mock_exists, mock_source_input
    ):
        mock_exists.return_value = True
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 0

    @patch("linkedin_post_generator.cli.generate_cmd._source_input", return_value=None)
    @patch("linkedin_post_generator.cli.generate_cmd.run_init")
    @patch("linkedin_post_generator.cli.generate_cmd.config_exists")
    def test_generate_triggers_init_when_no_config(
        self, mock_exists, mock_init, mock_source_input
    ):
        mock_exists.return_value = False
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 0
        assert mock_init.called
