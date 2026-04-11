# AGENTS.md — Coding Agent Instructions

## Build / Run / Test Commands

### Running the web-search script

```bash
# From skills/web-search/scripts/
python web_search.py tavily "query" [--max-results 5]
python web_search.py exa "query"
python web_search.py ollama "query"
```

Dependencies: `pip install httpx python-dotenv tavily-python ollama cyclopts exa-py pyyaml`

### No formal test suite or linter

This repository has **no test framework, no linter config, and no CI pipeline**. Before committing, manually verify:

- Markdown files render correctly
- Python scripts run without errors: `python web_search.py -h`
- SKILL.md frontmatter is valid YAML with `name`, `description`, and `license` fields

## Environment & Secrets

- API keys: `TAVILY_API_KEY`, `EXA_API_KEY`, `OLLAMA_API_KEY`

## Git

### Commit Message Format

Format: `<emoji> <short description>`

Rules:
- Use an emoji that matches the change type (e.g. 📝 docs, ✨ new feature, 🐛 fix, 🎨 style, 📊 charts, 🚫 init)
- Keep it short (one line, max ~50 chars)
- Accurately describe what changed in the files
- Use imperative mood, lowercase (e.g. "add", "fix", "update")
- **Write in English**

## Work In Progress (⚠️ Important!)

**The following skills are currently INCOMPLETE and should NOT be committed:**

- `activitywatch` - ActivityWatch time tracking skill (incomplete)
- `multi-agent-orchestration` - Multi-agent AI coordination skill (incomplete)  
- `rss-news` - RSS news aggregation skill (incomplete)

**DO NOT commit these skills until they are fully completed and reviewed.**

When working on skills:
1. Complete all skill content first
2. Test and verify the skill works
3. Commit skills individually (one skill per commit)
4. Only push when the skill is truly ready

## Common Tasks

### Authoring new skills

Read `SKILL-GUIDE.md` first. It covers the full template, frontmatter requirements, and reference file organization.

### Editing existing skills

1. Read the skill's `SKILL.md` first to understand the structure
2. Only load references relevant to your change — do not load all references
3. Follow the `❌`/`✅` comparison table pattern for error guidance
4. Verify frontmatter YAML is valid after edits

## Windows-Specific Notes

- Use PowerShell (pwsh) for shell commands
- Quote paths with spaces
