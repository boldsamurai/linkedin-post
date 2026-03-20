---
globs: ["linkedin_post_generator/ai/**", "linkedin_post_generator/templates/**"]
---

# Prompt Engineering Rules

## Prompt structure

Every generation prompt MUST follow this order:
1. **System message** — role definition + global constraints
2. **Template instructions** — specific to the selected template (Discovery, TIL, etc.)
3. **Source content** — fetched article text, GitHub README, or user's note
4. **User config context** — language, tone, target length, hashtags
5. **Output instructions** — format constraints, what NOT to do

## System message — editorial assistant role
- Role: "You are an editorial assistant helping the user write LinkedIn posts. You propose drafts that the user will review and edit."
- Framing: AI as collaborator, not impersonator — the user owns the voice
- Always include: "Write as if a real person is sharing their genuine perspective"
- Never: "You are a LinkedIn post writer" or "Write a LinkedIn post about..."

## Language handling
- ALWAYS specify target language explicitly: "Write entirely in Polish" or "Write entirely in English"
- Never mix languages in a single post
- Hashtags follow the post language, but tech terms stay in English (#Python, #DevOps)

## Tone instructions
Map tone enum to concrete, actionable prompt instructions:
- `professional-casual` → "Expert but approachable. No corporate jargon. First person. Share genuine opinion."
- `technical` → "Precise, data-driven. Include specific details, numbers, code references if relevant. Minimal fluff."
- `storytelling` → "Narrative structure. Start with a hook, build context, deliver insight. Personal experience angle."

Never use vague instructions like "be professional" — always specific.

## Length control
- Include character count target in prompt: "Target length: 800-1300 characters"
- Specify: "This is characters including spaces, not words."
- Short (500-800): one key insight, punchy
- Standard (800-1300): the LinkedIn sweet spot
- Long (1300-2000): more depth, still no fluff

## Source content — no hard limit
- **Articles**: readability extracts main content (no menus, ads) — send full extracted text
- **GitHub README**: full README + metadata (stars, language, topics, description). Truncate only if README >10k chars (keep first sections)
- **Notes**: send as-is, instruct AI to expand
- Prefer more context over less — AI needs to understand the source to write a good post

## Emoji policy
- Max 2-4 emoji per post
- Use as accents only: hook at the beginning, section dividers
- Never emoji in every sentence
- No emoji clusters (❌🔥💪🚀)

## Anti-patterns — NEVER include in generated posts
AI-slop openers:
- "In today's fast-paced world..."
- "I'm excited to share..."
- "As we navigate..."
- "Here's a comprehensive guide to..."

Engagement bait:
- "Agree? 👇" / "Thoughts? 👇" at the end
- Tagging people to force engagement
- "Repost if you agree"

Fake authenticity:
- Humble bragging ("Didn't expect my post to get 10k views...")
- Fake storytelling ("2 years ago I was at rock bottom. Today...")
- Sales pitch disguised as insight

Other:
- Hashtag spam — max 3-5 relevant hashtags at the end
- Generic conclusions that add nothing
- Lists of obvious advice ("1. Be consistent 2. Work hard 3. Never give up")

## Refinement — JSON conversation history
- Maintain conversation history as JSON array: `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]`
- First generation: save full prompt + AI response to JSON
- On refinement: append `{"role": "user", "content": "Modify the post: [feedback]"}` and send full history
- Pass entire conversation as context to `claude -p` — AI sees all previous iterations
- This works with both headless and API backends
- Instruction for refinement: "Modify the existing post based on this feedback. Keep everything else unchanged unless the feedback implies otherwise."
