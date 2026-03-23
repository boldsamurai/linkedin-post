"""Tests for AI response cleaning — strip conversation artifacts."""

from linkedin_post_generator.ai.cleaner import clean_ai_response


class TestCleanPrefixes:
    """Strip leading conversation artifacts."""

    def test_strips_heres_the_post(self) -> None:
        raw = "Here's the post:\n\nActual post content here."
        assert clean_ai_response(raw) == "Actual post content here."

    def test_strips_oto_post(self) -> None:
        raw = "Oto post na LinkedIn:\n\nTreść posta tutaj."
        assert clean_ai_response(raw) == "Treść posta tutaj."

    def test_strips_leading_separator(self) -> None:
        raw = "---\nPost content here."
        assert clean_ai_response(raw) == "Post content here."

    def test_strips_oto_wersja(self) -> None:
        raw = "Oto zmodyfikowana wersja:\n\nPoprawiony post."
        assert clean_ai_response(raw) == "Poprawiony post."

    def test_preserves_clean_text(self) -> None:
        raw = "Odkryłem świetne narzędzie do testowania."
        assert clean_ai_response(raw) == raw


class TestCleanSuffixes:
    """Strip trailing conversation artifacts."""

    def test_strips_trailing_separator_and_metadata(self) -> None:
        raw = "Post content.\n\n---\n\n📊 ~870 znaków, format Discovery."
        assert clean_ai_response(raw) == "Post content."

    def test_strips_character_count(self) -> None:
        raw = "Post content.\n\n📊 ~870 znaków (bez hashtagów)"
        assert clean_ai_response(raw) == "Post content."

    def test_strips_followup_pl(self) -> None:
        raw = "Post content.\n\nJeśli chcesz, mogę dostosować ton."
        assert clean_ai_response(raw) == "Post content."

    def test_strips_followup_en(self) -> None:
        raw = "Post content.\n\nLet me know if you want changes."
        assert clean_ai_response(raw) == "Post content."

    def test_strips_chcesz(self) -> None:
        raw = "Post content.\n\nChcesz zmodyfikować długość?"
        assert clean_ai_response(raw) == "Post content."

    def test_preserves_clean_ending(self) -> None:
        raw = "Post content.\n\n#Python #AI #DevOps"
        assert clean_ai_response(raw) == raw


class TestCleanCombined:
    """Both prefix and suffix artifacts."""

    def test_strips_both(self) -> None:
        raw = (
            "Oto post:\n\n"
            "Odkryłem świetne narzędzie!\n\n#Python"
            "\n\n---\n\n📊 ~500 znaków"
        )
        result = clean_ai_response(raw)
        assert result == "Odkryłem świetne narzędzie!\n\n#Python"

    def test_whitespace_handling(self) -> None:
        raw = "\n\n  Post content.  \n\n"
        assert clean_ai_response(raw) == "Post content."
