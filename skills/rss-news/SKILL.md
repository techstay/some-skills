---
name: rss-news
description: >
  RSS news aggregation skill. Fetches news by category from configured RSS
  sources and outputs each article as a title + summary block. Suitable for
  getting news updates, RSS feed subscriptions, blog or site updates, news
  source aggregation, and browsing news by category. The script ships with
  local caching (default 4 hours, adjustable) and by default only shows news
  from the last 24 hours, with filtering by category and time window.
license: MIT
version: "1.3.0"
---

# RSS News

Fetches news from RSS sources by category as defined in `news-source.json`, deduplicates via cache, and outputs each article as a title + summary block followed by a total count.

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

# Only refresh the cache, no news output (useful for warming cache)
uv run rss-fetch.py --fetch-only

# Force a cache refresh without outputting anything
uv run rss-fetch.py --fetch-only --refetch-interval-hours 0
```

---

## Command Options

| Option                       | Default      | Description                                                                                          |
| ---------------------------- | ------------ | ---------------------------------------------------------------------------------------------------- |
| `-c, --category`             | All categories | Categories to output, comma-separated, e.g. `-c politics,technology`. If omitted, outputs all available categories. |
| `--refetch-interval-hours`   | `4`          | Cache freshness threshold. Skips fetching when the cache exists and is younger than this many hours. |
| `--within-hours`             | `24`         | Only show news published within this many hours. `0` means no limit, showing all cached news.        |
| `--fetch-only`               | Off          | Only refresh the cache; do not output any news. Prints one status line to stdout on completion (`news fetched successfully` or `cache is fresh`). Respects `--refetch-interval-hours`; combine with `--refetch-interval-hours 0` to force a refresh. |
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
| Use `--fetch-only` to warm the cache       | Refreshes the cache without producing any news output; respects `--refetch-interval-hours` for freshness gating.            |
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

The script outputs each article as a **title + summary block**: the article title on the first line and the RSS summary text on the next line, blocks separated by a single blank line. A trailing `total n news` line reports how many articles were shown. Empty/whitespace-only summaries are skipped.

```
First article headline
First article's RSS summary text appears here.

Second article headline
Second article's RSS summary text appears here.

Third article headline
Third article's RSS summary text.

total 3 news
```

Field descriptions:

| Field    | Meaning                                                                               |
| -------- | ------------------------------------------------------------------------------------- |
| `title`  | The article title, printed as the first line of each block                            |
| `summary`| The RSS summary/description text of each article, HTML-stripped, on the line after the title |

---

## Caching

- Cache file: `cache/rss_output.json`
- Fetching uses HTTP `etag` / `modified` conditional requests; when a source returns 304, cached news is preserved and not wiped
- `last_sync` must reach `--refetch-interval-hours` (default 4 hours) before refetching
- Force refresh: `uv run rss-fetch.py --refetch-interval-hours 0`

---
