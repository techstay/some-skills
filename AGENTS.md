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

## Work In Progress (⚠️ Important!)

**The following skills are currently INCOMPLETE and should NOT be committed:**

- `activitywatch` - ActivityWatch time tracking skill (incomplete)

**DO NOT commit these skills until they are fully completed and reviewed.**

When working on skills:

1. Complete all skill content first
2. Test and verify the skill works
3. Commit skills individually (one skill per commit)
4. Only push when the skill is truly ready

## Common Tasks

### Editing existing skills

1. Read the skill's `SKILL.md` first to understand the structure
2. Only load references relevant to your change — do not load all references
3. Follow the `❌`/`✅` comparison table pattern for error guidance
4. Verify frontmatter YAML is valid after edits

## Windows-Specific Notes

- Use PowerShell (pwsh) for shell commands
- Quote paths with spaces
