---
name: web-search-skill
description: Web search, browsing, and citation workflow using multiple search backends (Tavily, Exa, Ollama) to answer time-sensitive or niche questions. Use when the user asks to search/browse/lookup, verify facts, get citations or quotes, find current info (news, prices, policies, schedules), or when uncertainty is high and web verification is needed.
---

# Web Search Skill

Run the CLI from `skills/web-search/scripts/`:

```bash
python web_search.py <subcommand> [options]
```

## Subcommands

| Subcommand | Backend    | Example                               |
| ---------- | ---------- | ------------------------------------- |
| `tavily`   | Tavily API | `python web_search.py tavily "query"` |
| `exa`      | Exa API    | `python web_search.py exa "query"`    |
| `ollama`   | Ollama     | `python web_search.py ollama "query"` |

Common option: `--max-results <N>` (default: `5`)

Results are returned as YAML texts. Set API keys in environment or `scripts/.env`:

```env
TAVILY_API_KEY=your_tavily_key
EXA_API_KEY=your_exa_key
OLLAMA_API_KEY=your_ollama_key
```
