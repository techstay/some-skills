# AGENTS.md — Coding Agent Instructions

You should always use English in codes and markdown files.

## Build / Run / Test Commands

You can use `uv run xxx.py` to run python scripts.

## Git

### Commit Message Format

Format: `<emoji> <short description>`

Rules:

- Use an emoji that matches the change type (e.g. 📝 docs, ✨ new feature, 🐛 fix, 🎨 style, 📊 charts)
- Keep it short (one line, max ~50 chars)
- Accurately describe what changed in the files
- Use imperative mood, lowercase (e.g. "add", "fix", "update")
- **Write in English**

## Common Tasks

### Editing existing skills

1. Read the skill's `SKILL.md` first to understand the structure
2. Only load references relevant to your change — do not load all references
3. Follow the `❌`/`✅` comparison table pattern for error guidance
4. Verify frontmatter YAML is valid after edits

## Markdown Files

- Write all Markdown files in English (see the rule at the top of this file).
- After editing a Markdown file, format it with Prettier before considering the change done:

  ```sh
  bunx prettier --write path/to/file.md
  ```

- Project-wide Markdown lint rules are defined in `.markdownlint.json` (e.g. MD033 inline-HTML is allowed).

## Windows-Specific Notes

- Use PowerShell (pwsh) for shell commands
- Quote paths with spaces
