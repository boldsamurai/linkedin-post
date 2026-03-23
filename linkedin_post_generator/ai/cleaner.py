"""Post-processing — strip common AI conversation artifacts from generated text."""

import re

# Patterns to strip from the beginning of AI responses
_PREFIX_PATTERNS = [
    # "Here's the post:", "Oto post na LinkedIn:", "Sure! Here's a draft:"
    re.compile(
        r"^.{0,100}(post|draft|wersja|version|LinkedIn)[:\.]?\s*\n+",
        re.IGNORECASE,
    ),
    # Leading "---" separator
    re.compile(r"^-{3,}\s*\n+"),
]

# Patterns to strip from the end of AI responses
_SUFFIX_PATTERNS = [
    # Trailing "---" separator and everything after
    re.compile(r"\n+-{3,}\s*\n.*$", re.DOTALL),
    # Character count metadata: "📊 ~870 znaków..."
    re.compile(r"\n+📊.*$", re.DOTALL),
    # Follow-up offers: "Jeśli chcesz...", "Let me know...", etc.
    re.compile(
        r"\n{2,}(Jeśli chcesz|If you|Want me|Let me know"
        r"|Mogę|Chcesz|Daj znać).*$",
        re.DOTALL | re.IGNORECASE,
    ),
]


def clean_ai_response(text: str) -> str:
    """Strip common AI conversation artifacts from generated post text.

    Removes leading introductions ("Here's the post:"), trailing
    metadata ("~870 chars"), separators (---), and follow-up offers.

    Args:
        text: Raw AI response text.

    Returns:
        Cleaned post text.
    """
    result = text.strip()

    for pattern in _PREFIX_PATTERNS:
        result = pattern.sub("", result, count=1).lstrip()

    for pattern in _SUFFIX_PATTERNS:
        result = pattern.sub("", result).rstrip()

    return result.strip()
