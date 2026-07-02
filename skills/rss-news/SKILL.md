---
name: rss-news
description: >
  RSS news aggregation skill. Fetches news by category from configured RSS
  sources and outputs in YAML format. Suitable for getting news updates, RSS
  feed subscriptions, blog or site updates, news source aggregation, and
  browsing news by category. The script ships with local caching (default 4
  hours, adjustable) and by default only shows news from the last 24 hours,
  with filtering by category and time window.
license: MIT
version: "1.0.0"
---

# RSS News

Fetches news from RSS sources by category as defined in `news-source.json`, deduplicates via cache, and outputs in YAML format.

## Quick Reference

```bash
cd skills/rss-news/scripts

# Without -c, all available categories are fetched by default
uv run rss-fetch.py

# Single category
uv run rss-fetch.py -c politics
uv run rss-fetch.py -c technology

# Multiple categories (comma-separated)
uv run rss-fetch.py -c politics,technology

# Only news from the last 48 hours (default 24, 0 means no time limit)
uv run rss-fetch.py -c politics --within-hours 48
uv run rss-fetch.py -c sports --within-hours 0
```

---

## Command Options

| Option                       | Default      | Description                                                                                          |
| ---------------------------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| `-c, --category`             | All categories | Categories to output, comma-separated, e.g. `-c politics,technology`. If omitted, outputs all available categories. |
| `--refetch-interval-hours`   | `4`          | Cache freshness threshold. Skips fetching when the cache exists and is younger than this many hours. |
| `--within-hours`             | `24`         | Only show news published within this many hours. `0` means no limit, showing all cached news.        |
| `--debug`                    | Off          | Enables DEBUG-level logging, outputting fetch and cache details.                                     |
| `-h, --help`                 | —            | Show help.                                                                                           |
| `--version`                  | —            | Show version.                                                                                        |

---

## Key Rules

| Rule                                       | Description                                                                                                                |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Use `-c` to select categories, omit for all | Category names are listed in the table below; comma-separate for multiple selections.                                      |
| Cache is managed automatically             | `cache/rss_output.json` skips fetching if younger than `--refetch-interval-hours`; auto-refreshes fully when stale or missing. |
| Use `--within-hours` to control time range | Defaults to showing only news from the last 24 hours; pass `0` to show all.                                                |
| Do not manually look for a refresh command | Refresh logic is built into the output flow; pass `--refetch-interval-hours 0` to force a refresh.                         |
| The script only returns RSS summaries      | When full article text is needed, fetch the `link` with a web tool.                                                        |
| Fetch failures do not halt execution       | A single source failure is logged and skipped; other sources return normally.                                              |

---

## Available Categories

Categories are defined by the script's `Category` enum and map to category names in `news-source.json`:

| Category name (`-c` value) | Maps to `news-source.json` category |
| -------------------------- | ----------------------------------- |
| `china`                    | China News                          |
| `international`            | International News                  |
| `technology`               | Technology                          |
| `finance`                  | Business & Finance                  |
| `politics`                 | Politics                            |
| `sports`                   | Sports                              |
| `science`                  | Science                             |
| `health`                   | Health & Medicine                   |
| `entertainment`            | Entertainment                       |
| `culture`                  | Culture & Education                 |

---

## Output Format

The script outputs YAML-style text (top level is `last_sync` / `article_count` / `categories`):

```yaml
last_sync: "2026-07-02T10:00:00+08:00"
article_count: 2
categories:
  Politics:
    - title: "Example headline"
      link: "https://example.com/article"
      summary: "RSS summary text"
      published: "2026-07-02T07:30:00+00:00"
      source: "Politico"
  Technology:
    - title: "Another headline"
      link: "https://example.com/tech-article"
      summary: "RSS summary text"
      published: "2026-07-02T06:00:00+00:00"
      source: "The Verge"
```

Field descriptions:

| Field                                                 | Meaning                                                                  |
| ----------------------------------------------------- | ------------------------------------------------------------------------ |
| `last_sync`                                           | Time of the most recent cache fetch (Asia/Shanghai timezone)             |
| `article_count`                                       | Total number of news items in this output (after category/time filtering) |
| `categories`                                          | News lists grouped by category name; each category contains an array of articles |
| `title` / `link` / `summary` / `published` / `source` | Per-article title, link, summary, publish time (ISO 8601), and source display name |

---

## Caching

- Cache file: `cache/rss_output.json`
- Fetching uses HTTP `etag` / `modified` conditional requests; when a source returns 304, cached news is preserved and not wiped
- `last_sync` must reach `--refetch-interval-hours` (default 4 hours) before refetching
- Force refresh: `uv run rss-fetch.py --refetch-interval-hours 0`

---
