"""Prompt assembly — builds system prompts and user messages for AI generation."""

from linkedin_post_generator.config.model import Language, Length, Tone

SYSTEM_PROMPT_BASE = (
    "You are an editorial assistant helping the user write LinkedIn posts. "
    "You propose drafts that the user will review and edit.\n"
    "Write as if a real person is sharing their genuine perspective."
)

TONE_INSTRUCTIONS: dict[Tone, str] = {
    Tone.PROFESSIONAL_CASUAL: (
        "Expert but approachable. No corporate jargon. First person. "
        "Share genuine opinion."
    ),
    Tone.TECHNICAL: (
        "Precise, data-driven. Include specific details, numbers, "
        "code references if relevant. Minimal fluff."
    ),
    Tone.STORYTELLING: (
        "Narrative structure. Start with a hook, build context, "
        "deliver insight. Personal experience angle."
    ),
}

LENGTH_RANGES: dict[Length, tuple[int, int]] = {
    Length.SHORT: (500, 800),
    Length.STANDARD: (800, 1300),
    Length.LONG: (1300, 2000),
}

LANGUAGE_INSTRUCTIONS: dict[Language, str] = {
    Language.PL: (
        "Write the ENTIRE post in Polish. "
        "Even if the source material is in English, the post MUST be in Polish. "
        "Translate and adapt — do not copy English text into the post."
    ),
    Language.EN: (
        "Write the ENTIRE post in English. "
        "Even if the source material is in another language, "
        "the post MUST be in English."
    ),
}

ANTI_PATTERNS = """\
NEVER use these patterns in the post:
- AI-slop openers: "In today's fast-paced world...", "I'm excited to share...", \
"As we navigate...", "Here's a comprehensive guide to..."
- Engagement bait: "Agree? 👇", "Thoughts? 👇", "Repost if you agree"
- Fake authenticity: humble bragging, fake storytelling ("2 years ago I was at \
rock bottom..."), sales pitch disguised as insight
- Generic conclusions that add nothing
- Lists of obvious advice ("1. Be consistent 2. Work hard 3. Never give up")\
"""

EMOJI_POLICY = (
    "Use max 2-4 emoji per post. "
    "Use them as accents only: hook at the beginning, section dividers. "
    "Never emoji in every sentence. No emoji clusters."
)

HASHTAG_POLICY = (
    "Place 3-5 relevant hashtags at the end of the post. "
    "Tech terms stay in English (#Python, #DevOps) regardless of post language."
)

OUTPUT_FORMAT = """\
CRITICAL: Output ONLY the raw post text. Nothing else.

DO NOT include:
- Any introduction ("Here's the post:", "Oto post:", "Sure!", etc.)
- Any separators (---, ***, ===)
- Any metadata or character counts ("~870 znaków", "format Discovery")
- Any follow-up questions ("Chcesz zmienić...?", "Let me know if...")
- Any markdown formatting (**, ##, etc.)

LinkedIn accepts plain text only. Your entire response must be \
the post itself — ready to paste directly on LinkedIn.\
"""


def build_system_prompt(
    template_instructions: str,
    tone: Tone,
    language: Language,
    length: Length,
    hashtags: list[str] | None = None,
) -> str:
    """Assemble a full system prompt from components.

    Follows the prompt structure defined in rules/prompts.md:
    1. Role definition + global constraints
    2. Template-specific instructions
    3. User config context (language, tone, length, hashtags)
    4. Output instructions (format, anti-patterns)

    Args:
        template_instructions: Template-specific prompt snippet (e.g. Discovery focus).
        tone: Writing tone from config.
        language: Target language from config.
        length: Target post length from config.
        hashtags: Default hashtags from config (optional).

    Returns:
        Complete system prompt string.
    """
    char_min, char_max = LENGTH_RANGES[length]

    sections = [
        # 1. Role
        SYSTEM_PROMPT_BASE,
        # 2. Template instructions
        f"## Post style\n{template_instructions}",
        # 3. Config context
        f"## Language\n{LANGUAGE_INSTRUCTIONS[language]}",
        f"## Tone\n{TONE_INSTRUCTIONS[tone]}",
        (
            f"## Length\n"
            f"Target length: {char_min}-{char_max} characters "
            f"(including spaces, not words)."
        ),
        f"## Emoji\n{EMOJI_POLICY}",
    ]

    # Hashtags section
    if hashtags:
        tags = ", ".join(hashtags)
        sections.append(
            f"## Hashtags\n{HASHTAG_POLICY}\nAlways include these hashtags: {tags}"
        )
    else:
        sections.append(f"## Hashtags\n{HASHTAG_POLICY}")

    # 4. Output instructions
    sections.append(f"## Output format\n{OUTPUT_FORMAT}")
    sections.append(f"## Anti-patterns\n{ANTI_PATTERNS}")

    return "\n\n".join(sections)


def build_user_message(source_content: str) -> str:
    """Wrap source content as the user message for generation.

    Args:
        source_content: The fetched source text (article, README, note).

    Returns:
        User message string ready to send to AI.
    """
    return (
        "Write a LinkedIn post based on the following source material:\n\n"
        f"---\n{source_content}\n---"
    )
