"""Built-in LinkedIn post templates — registered on import."""

from linkedin_post_generator.templates.models import PostTemplate
from linkedin_post_generator.templates.registry import register

DISCOVERY = register(
    PostTemplate(
        name="discovery",
        label="Discovery",
        description="I found this, here's why it matters to you",
        instructions=(
            "Write a post about discovering something valuable — a tool, library, "
            "project, or resource.\n\n"
            "Structure:\n"
            "1. Hook — grab attention with what you found\n"
            "2. What it is — brief, clear explanation\n"
            "3. Why it's interesting — the value proposition, what problem it solves\n"
            "4. Your take — personal perspective on why it matters\n"
            "5. Soft call to action — invite readers to check it out\n\n"
            "Keep the tone of genuine enthusiasm — you found something useful and "
            "want to share it, not sell it."
        ),
    )
)

OPINION = register(
    PostTemplate(
        name="opinion",
        label="Opinion",
        description="Here's my take, agree or disagree",
        instructions=(
            "Write an opinion post that takes a clear stance on a topic.\n\n"
            "Structure:\n"
            "1. Bold statement — lead with your opinion, no hedging\n"
            "2. Context — why this matters, what triggered the thought\n"
            "3. Argumentation — support your position with experience or evidence\n"
            "4. Nuance — acknowledge complexity without retreating from your stance\n"
            "5. Open question — invite genuine discussion, not engagement bait\n\n"
            "The opinion must feel earned through experience, not contrarian for "
            "attention. Avoid 'unpopular opinion:' framing."
        ),
    )
)

TIL = register(
    PostTemplate(
        name="til",
        label="TIL",
        description="Short, punchy technical insight",
        instructions=(
            "Write a 'Today I Learned' post — a concise technical insight.\n\n"
            "Structure:\n"
            "1. The insight — what you learned, stated clearly\n"
            "2. Context — how you discovered it "
            "(debugging, code review, reading docs)\n"
            "3. Practical takeaway — how others can use this knowledge\n\n"
            "Keep it short and punchy — this format works best at 500-800 characters. "
            "One key insight, not a tutorial. Show the 'aha!' moment."
        ),
    )
)

PROJECT_SHOWCASE = register(
    PostTemplate(
        name="project-showcase",
        label="Project Showcase",
        description="I built this, here's the journey",
        instructions=(
            "Write a post showcasing a project — yours or one you contributed to.\n\n"
            "Structure:\n"
            "1. The problem — what pain point or need motivated this\n"
            "2. The solution — what was built and how it works (high level)\n"
            "3. What you learned — honest reflection on the journey\n"
            "4. Link/invitation — where to find it, how to try it\n\n"
            "Focus on the story and lessons, not feature lists. "
            "Be honest about challenges — 'it was easy' is never interesting. "
            "Show the human behind the code."
        ),
    )
)

ARTICLE_REACTION = register(
    PostTemplate(
        name="article-reaction",
        label="Article Reaction",
        description="Read this, here's what stood out",
        instructions=(
            "Write a reaction post about an article, blog post, or piece of content "
            "you read.\n\n"
            "Structure:\n"
            "1. Reference — what you read (title, author if known)\n"
            "2. Key insight — the one thing that stood out most\n"
            "3. Your perspective — how this connects to your experience\n"
            "4. Recommendation — why others should read it\n\n"
            "Add your own perspective — don't just summarize the article. "
            "The value is in YOUR reaction, not the summary. "
            "Disagree with something? Even better."
        ),
    )
)
