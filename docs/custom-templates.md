# Custom templates

Besides the five built-in templates (Discovery, Opinion, TIL, Project Showcase,
Article Reaction) you can add your own. Each custom template is one TOML file; it
shows up in the template menu of `linkedin-post generate` marked with 🧩, after the
built-ins.

## Where the files go

Put the files in a `templates` directory inside the config directory:

| OS      | Directory                                               |
|---------|---------------------------------------------------------|
| Linux   | `~/.config/linkedin-post/templates/`                    |
| macOS   | `~/Library/Application Support/linkedin-post/templates/` |
| Windows | `%LOCALAPPDATA%\linkedin-post\linkedin-post\templates\` |

The tool never creates this directory — make it yourself. A missing directory
simply means there are no custom templates. Only files ending in `.toml` are read,
in file-name order; any other file is ignored.

## Fields

Every file must define all four fields, and none of them may be empty:

| Field          | What it is                                                                                     |
|----------------|------------------------------------------------------------------------------------------------|
| `name`         | Identifier: lowercase letters, digits and `-` only (e.g. `weekly-digest`). Must be unique.      |
| `label`        | Name shown in the menu (🧩 is added in front automatically).                                   |
| `description`  | One-line description shown next to the label in the menu.                                      |
| `instructions` | Instructions for the AI: what this kind of post does and how to structure it.                   |

`name` cannot reuse a built-in template's name (`discovery`, `opinion`, `til`,
`project-showcase`, `article-reaction`) or the name of another custom file.

Language, tone, length and hashtags are not part of a template — they come from your
config and the choices you make during `generate`, exactly as with built-in
templates. Write `instructions` in English; the post language is set separately.

## Example

`~/.config/linkedin-post/templates/lesson-learned.toml`:

```toml
name = "lesson-learned"
label = "Lesson learned"
description = "A mistake from a project and what it taught me"
instructions = """
Structure the post around one concrete mistake taken from the source.
1. Open with the moment the problem became visible — no generic intro.
2. Explain the cause in one or two sentences, with a specific technical detail.
3. Describe what was changed afterwards.
4. End with the single lesson a reader can apply in their own work.
Keep it honest: no hindsight heroics, no blame.
"""
```

Run `linkedin-post generate`, and "🧩 Lesson learned" appears in the template menu.

## When a file is broken

Template files are validated whenever the template list is read. If any file is
broken, `generate` stops with an error naming the file and the reason instead of
silently skipping it:

- the file cannot be read, is not valid TOML, or is not UTF-8 text,
- a field is missing, empty or not a string,
- `name` contains characters other than `a-z`, `0-9` and `-`,
- `name` clashes with a built-in template or another file.

Fix or remove the file and run the command again.
