---
name: search-and-extract
description: >
  Web search and content extraction skill spanning Tavily, Exa, Ollama Cloud,
  Jina AI, Parallel Web Systems, Firecrawl, and local SearXNG. Use when the user
  asks to search the web, fetch a page, verify facts, gather citations, or
  extract article text for LLM consumption.
---

# Search and Extract

A single-file CLI for web search and URL content extraction across multiple
services. Output is plain text (`\n---\n` separated) intended for LLM consumption.

## Quick Reference

```bash
cd skills/search-and-extract/scripts

# Search — pick a backend with a --<service> flag (defaults to 10 results)
uv run search-extract.py search --tavily "latest rust release"
uv run search-extract.py search --exa "quantum computing"
uv run search-extract.py search --ollama "open source LLMs"
uv run search-extract.py search --jina "climate news"
uv run search-extract.py search --searxng "news today"

# No --<service> flag? The first available service is used automatically.
uv run search-extract.py search "latest AI news"

# Extract — same flag pattern, takes a single URL
uv run search-extract.py extract --tavily https://example.com
uv run search-extract.py extract --exa https://example.com
uv run search-extract.py extract --ollama https://example.com
uv run search-extract.py extract --jina https://example.com
uv run search-extract.py extract https://example.com   # default to first available
```

---

## Service selection

Pick a backend by passing exactly one `--<service>` flag. If no service flag is
given, the CLI auto-selects the **first available** service (in the order below)
that is enabled and has its required API key set.

| Priority | Service   | `search` | `extract` | Required key        |
| -------- | --------- | :------: | :-------: | ------------------- |
| 1        | `tavily`  | yes      | yes       | `TAVILY_API_KEY`    |
| 2        | `exa`     | yes      | yes       | `EXA_API_KEY`       |
| 3        | `ollama`  | yes      | yes       | `OLLAMA_API_KEY`    |
| 4        | `jina`    | yes      | yes       | key optional        |
| 5        | `searxng` | yes      | no        | none (local server) |
| 6        | `parallel`| yes      | yes       | `PARALLEL_API_KEY`  |
| 7        | `firecrawl`| yes     | yes       | key optional        |

> Passing more than one `--<service>` flag is an error. Diagnostics (default
> selection, errors) go to **stderr** so **stdout** stays clean for LLM use.

---

## Commands

### `search <query> [--<service>] [--max-results N]`

Search the web. `<query>` is positional; the backend is chosen with a
`--<service>` flag (default: first available). Returns up to `N` results
(default `10`).

| Flag              | Description                                            |
| ----------------- | ------------------------------------------------------ |
| `--tavily`        | Tavily API, optional answer prepended                  |
| `--exa`           | Exa neural search, returns highlights                  |
| `--ollama`        | Ollama Cloud                                           |
| `--jina`          | Jina AI, key optional                                  |
| `--searxng`       | Local SearXNG instance (search only)                   |
| `--parallel`      | Parallel Web Systems, returns excerpts                 |
| `--firecrawl`     | Firecrawl, key optional                                |
| `--max-results N` | Max results to return (default `10`)                   |

### `extract <url> [--<service>]`

Extract content from a single URL. `<url>` is positional; the backend is chosen
with a `--<service>` flag (default: first available). All backends take exactly
one URL.

| Flag          | Description                              |
| ------------- | ---------------------------------------- |
| `--tavily`    | Tavily, markdown output                  |
| `--exa`       | Exa, full text                           |
| `--ollama`    | Ollama Cloud                             |
| `--jina`      | Jina AI                                  |
| `--parallel`  | Parallel Web Systems, full content       |
| `--firecrawl` | Firecrawl, markdown via scrape           |

---

## Core function signatures

Each backend is a plain function with a normalized parameter list:

| Function           | Signature                          |
| ------------------ | ---------------------------------- |
| `*_search`         | `(query: str, max_results=10)`     |
| `*_extract`        | `(url: str)`                       |

Search functions take only the result count (`max_results`, default `10`) beyond
the query. Extract functions take only a single `url`.

---

## Environment Variables

| Variable         | Required | Default                  | Description                             |
| ---------------- | -------- | ------------------------ | --------------------------------------- |
| `TAVILY_API_KEY` | Tavily   | —                        | API key for Tavily search/extract       |
| `EXA_API_KEY`    | Exa      | —                        | API key for Exa search/extract          |
| `OLLAMA_API_KEY` | Ollama   | —                        | API key for Ollama Cloud                |
| `JINA_API_KEY`     | Optional | —                        | Optional key for higher Jina rate limit |
| `SEARXNG_URL`      | SearXNG  | `http://localhost:8888`  | Base URL of local SearXNG instance      |
| `PARALLEL_API_KEY` | Parallel | —                        | API key for Parallel search/extract     |
| `FIRECRAWL_API_KEY`| Optional | —                        | Optional key for Firecrawl rate limits  |
| `DISABLE_TAVILY` | No       | —                        | Set `1` or `true` to skip Tavily        |
| `DISABLE_EXA`    | No       | —                        | Set `1` or `true` to skip Exa           |
| `DISABLE_OLLAMA` | No       | —                        | Set `1` or `true` to skip Ollama        |
| `DISABLE_JINA`     | No       | —                        | Set `1` or `true` to skip Jina          |
| `DISABLE_SEARXNG`  | No       | —                        | Set `1` or `true` to skip SearXNG       |
| `DISABLE_PARALLEL` | No       | —                        | Set `1` or `true` to skip Parallel      |
| `DISABLE_FIRECRAWL`| No       | —                        | Set `1` or `true` to skip Firecrawl     |

A service counts as **available** for default selection only if it is not
disabled **and** has its required key set (where one is required).

---

## Notes

- Output is plain text meant for LLM consumption; multiple results are separated by `\n---\n`.
- Missing required keys or disabled services return short error strings instead of crashing.
- SearXNG only supports `search`; there is no `--searxng` flag for `extract`.
- Jina AI and Firecrawl work without an API key at a lower rate limit.
- Search defaults to 10 results; `--max-results` overrides it.
- `extract` takes exactly one URL per invocation.
- Run with `uv run search-extract.py ...` so PEP 723 inline dependencies are resolved automatically.
