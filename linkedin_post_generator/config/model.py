"""Pydantic config model with enums and sensible defaults."""

from enum import StrEnum

from pydantic import BaseModel, Field


class Language(StrEnum):
    PL = "pl"
    EN = "en"


class Tone(StrEnum):
    PROFESSIONAL_CASUAL = "professional-casual"
    TECHNICAL = "technical"
    STORYTELLING = "storytelling"


class Length(StrEnum):
    SHORT = "short"
    STANDARD = "standard"
    LONG = "long"


class AIBackend(StrEnum):
    AUTO = "auto"
    HEADLESS = "headless"
    API = "api"


class AppConfig(BaseModel):
    """Application configuration with sensible defaults."""

    language: Language = Field(
        default=Language.PL,
        description="Default post language",
    )
    tone: Tone = Field(
        default=Tone.PROFESSIONAL_CASUAL,
        description="Default writing tone",
    )
    length: Length = Field(
        default=Length.STANDARD,
        description="Default post length",
    )
    hashtags: list[str] = Field(
        default_factory=list,
        description="Default hashtags to suggest",
    )
    ai_backend: AIBackend = Field(
        default=AIBackend.AUTO,
        description="AI backend: auto, headless (Claude CLI), or api",
    )
