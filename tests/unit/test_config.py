"""Tests for the config module — model, reader, writer, fallback chain."""

import tomllib

import pytest
import tomli_w

from linkedin_post_generator.config.model import (
    AIBackend,
    AppConfig,
    Language,
    Length,
    Tone,
)
from linkedin_post_generator.config.reader import load_config
from linkedin_post_generator.config.writer import save_config


class TestAppConfig:
    """Tests for the Pydantic config model."""

    def test_defaults(self):
        config = AppConfig()
        assert config.language == Language.PL
        assert config.tone == Tone.PROFESSIONAL_CASUAL
        assert config.length == Length.STANDARD
        assert config.hashtags == []
        assert config.ai_backend == AIBackend.AUTO

    def test_all_fields_from_dict(self):
        data = {
            "language": "en",
            "tone": "technical",
            "length": "long",
            "hashtags": ["#Python", "#DevOps"],
            "ai_backend": "api",
        }
        config = AppConfig(**data)
        assert config.language == Language.EN
        assert config.tone == Tone.TECHNICAL
        assert config.length == Length.LONG
        assert config.hashtags == ["#Python", "#DevOps"]
        assert config.ai_backend == AIBackend.API

    def test_partial_fields_use_defaults(self):
        config = AppConfig(language="en")
        assert config.language == Language.EN
        assert config.tone == Tone.PROFESSIONAL_CASUAL  # default

    def test_invalid_language_raises(self):
        with pytest.raises(ValueError, match="Input should be"):
            AppConfig(language="de")

    def test_invalid_tone_raises(self):
        with pytest.raises(ValueError, match="Input should be"):
            AppConfig(tone="aggressive")

    def test_invalid_length_raises(self):
        with pytest.raises(ValueError, match="Input should be"):
            AppConfig(length="huge")

    def test_invalid_backend_raises(self):
        with pytest.raises(ValueError, match="Input should be"):
            AppConfig(ai_backend="openai")


class TestConfigWriter:
    """Tests for saving config to TOML."""

    def test_save_creates_file(self, tmp_path):
        config = AppConfig(language="en", hashtags=["#AI"])
        target = tmp_path / "config.toml"
        result = save_config(config, path=target)

        assert result == target
        assert target.is_file()

    def test_save_roundtrip(self, tmp_path):
        config = AppConfig(
            language="en",
            tone="technical",
            length="long",
            hashtags=["#Python", "#CLI"],
            ai_backend="api",
        )
        target = tmp_path / "config.toml"
        save_config(config, path=target)

        with target.open("rb") as f:
            data = tomllib.load(f)

        assert data["language"] == "en"
        assert data["tone"] == "technical"
        assert data["length"] == "long"
        assert data["hashtags"] == ["#Python", "#CLI"]
        assert data["ai_backend"] == "api"

    def test_save_creates_parent_dirs(self, tmp_path):
        target = tmp_path / "deep" / "nested" / "config.toml"
        save_config(AppConfig(), path=target)
        assert target.is_file()


class TestConfigReader:
    """Tests for TOML reading and fallback chain."""

    def test_load_defaults_when_no_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "linkedin_post_generator.config.reader.global_config_path",
            lambda: tmp_path / "nonexistent.toml",
        )
        monkeypatch.setattr(
            "linkedin_post_generator.config.reader.local_config_path",
            lambda: None,
        )
        config = load_config()
        assert config == AppConfig()

    def test_load_from_global(self, tmp_path, monkeypatch):
        global_file = tmp_path / "global.toml"
        with global_file.open("wb") as f:
            tomli_w.dump({"language": "en", "tone": "technical"}, f)

        monkeypatch.setattr(
            "linkedin_post_generator.config.reader.global_config_path",
            lambda: global_file,
        )
        monkeypatch.setattr(
            "linkedin_post_generator.config.reader.local_config_path",
            lambda: None,
        )
        config = load_config()
        assert config.language == Language.EN
        assert config.tone == Tone.TECHNICAL
        assert config.length == Length.STANDARD  # default

    def test_local_overrides_global(self, tmp_path, monkeypatch):
        global_file = tmp_path / "global.toml"
        local_file = tmp_path / "local.toml"

        with global_file.open("wb") as f:
            tomli_w.dump({"language": "en", "tone": "technical"}, f)
        with local_file.open("wb") as f:
            tomli_w.dump({"language": "pl"}, f)

        monkeypatch.setattr(
            "linkedin_post_generator.config.reader.global_config_path",
            lambda: global_file,
        )
        monkeypatch.setattr(
            "linkedin_post_generator.config.reader.local_config_path",
            lambda: local_file,
        )
        config = load_config()
        assert config.language == Language.PL  # local override
        assert config.tone == Tone.TECHNICAL  # from global

    def test_load_ignores_malformed_toml(self, tmp_path, monkeypatch):
        bad_file = tmp_path / "bad.toml"
        bad_file.write_text("this is not valid toml [[[", encoding="utf-8")

        monkeypatch.setattr(
            "linkedin_post_generator.config.reader.global_config_path",
            lambda: bad_file,
        )
        monkeypatch.setattr(
            "linkedin_post_generator.config.reader.local_config_path",
            lambda: None,
        )
        config = load_config()
        assert config == AppConfig()  # falls back to defaults

    def test_cross_platform_paths_resolve(self):
        """Verify path functions return Path objects (basic smoke test)."""
        from linkedin_post_generator.config.paths import (
            config_dir,
            global_config_path,
            history_db_path,
        )

        assert config_dir().is_absolute()
        assert global_config_path().name == "config.toml"
        assert history_db_path().name == "history.db"
