# 🛠️ some-skills

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=techstay.some-skills&left_color=555&right_color=e74c3c&left_text=visitors" alt="visitors" />
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License: MIT" /></a>
  <a href="https://github.com/techstay/some-skills"><img src="https://img.shields.io/badge/GitHub-repo-181717?style=flat-square&logo=github" alt="GitHub" /></a>
  <img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4-red?style=flat-square" alt="Made with love" />
</p>

A collection of useful skills for extending AI coding agent capabilities. Each skill packages domain knowledge, reference materials, and executable scripts into a self-contained unit that agents can load on demand.

<!--Quote starts-->
<details>
<summary><b>💡 Daily Inspiration</b></summary>

<img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=light" alt="Random Quote" />

</details>
<!--Quote ends-->

## 🚀 Installation

Skills in this repository can be installed to various AI coding agents (OpenCode, Claude Code, Cursor, Codex, and 40+ more) via the `npx skills` CLI tool.

### Quick Start

```bash
# Install all skills to project
npx skills add techstay/some-skills

# Install globally
npx skills add techstay/some-skills -g

# Install specific skills
npx skills add techstay/some-skills --skill rss-news --skill search-and-extract

# Install for specific agents
npx skills add techstay/some-skills -a opencode -a claude-code

# List available skills without installing
npx skills add techstay/some-skills --list
```

### More Commands

| Command | Description |
|---------|-------------|
| `npx skills list` | List installed skills |
| `npx skills find [query]` | Search for skills |
| `npx skills remove [skills]` | Remove installed skills |
| `npx skills check` | Check for skill updates |
| `npx skills update` | Update all installed skills |

> Learn more: [vercel-labs/skills](https://github.com/vercel-labs/skills)

## 📁 Skill Catalog

### 🔍 search-and-extract

Web search and URL content extraction CLI spanning multiple backends to answer time-sensitive or niche questions. Use for fact verification, getting citations/quotes, finding current information (news, prices, policies, schedules), fetching article text, or whenever uncertainty is high and web verification is needed.

**Features:**

- Seven backends: Tavily, Exa, Ollama Cloud, Jina AI, Parallel Web Systems, Firecrawl, and local SearXNG
- Two commands: `search` (web search) and `extract` (fetch a single URL)
- Auto-selects first available backend; override with `--<service>` flag
- Configurable result limit (`--max-results`, default 10)
- Plain text output (`\n---\n` separated) optimized for LLM consumption
- API keys configured via environment variables

### 🗞️ rss-news

RSS news aggregation skill that fetches news by category from configured RSS sources and outputs structured YAML results. Features local caching, deduplication, and time-window filtering.

**Features:**

- 10 news categories: China, International, Technology, Finance, Politics, Sports, Science, Health, Entertainment, Culture
- Configurable time window (`--within-hours`, default 24h)
- Smart 4-hour caching with HTTP conditional requests (ETag/Last-Modified)
- Fault-tolerant fetching (individual source failures don't halt execution)
- Pre-configured sources including major Chinese and international outlets
- `--fetch-only` mode for cache warming without output
- Debug mode for troubleshooting

### 📂 jellyfin-renaming

Guided, manually-reviewed workflow for renaming movies, TV shows, anime, specials, external subtitles, external audio tracks, and their containing folders to match Jellyfin naming conventions. Every rename is reviewed before execution — nothing is applied blindly.

**Features:**

- Two modes: dry-run (suggest names only) and apply (rename on disk after review)
- Absolute no-delete safety: files are moved to a `Rubbish/` subfolder instead of being removed
- Deepest-path-first rename order with case-insensitive filesystem handling
- Automatic append-only `rename-log.md` recording every rename
- Comprehensive Jellyfin naming rules covering: movies (with TMDB/IMDb IDs), multi-version files, 3D movies, multi-part movies, TV seasons/episodes, multi-episode files, specials (Season 00), anime extras (NCOP/NCED/OVA/OAD/SP), external subtitles/audio with language/flag tags, extras/trailers, and local artwork
- Built-in TMDB metadata lookup helper to confirm titles, years, and IDs
- Quality checklist for verifying rename correctness

### 🔔 push-and-notify

Send push notifications to multiple messaging endpoints from a single unified CLI. Supports Telegram, ntfy, and WxPusher (WeChat push) as independent subcommands — credentials are only needed for the services you use.

**Features:**

- Three notification services in one tool:
  - **Telegram** — via Telegram Bot API
  - **ntfy** — via ntfy topics (supports custom servers and auth tokens)
  - **WxPusher** — WeChat push notifications (supports multiple recipients)
- Multi-line content normalization (handles Windows/Mac/Unix line endings and escaped newlines)
- Uniform CLI interface: `uv run notify.py <service> <title> <content>`
- YAML-formatted success/failure status output; errors go to stderr via loguru
- Each service's credentials are independently configured via `.env`

### 📓 marimo

Create and manage reactive Python notebooks in Marimo — an open-source reactive notebook that reimagines Jupyter as reproducible, interactive, shareable Python programs.

**Features:**

- Covers notebook creation, UI input components (`mo.ui.*`), SQL cells, and app deployment
- DAG-based reactive execution model reference
- Common pitfalls guide with ❌/✅ comparisons (mutation tracking, global variable uniqueness)
- Quick reference table for daily tasks
- 5 reference documents covering:
  - Core concepts (reactive execution, DAG, static analysis)
  - UI input components
  - SQL and data processing
  - App deployment and layout options
  - CLI commands reference

### ⏱️ activitywatch

Retrieve and analyze local ActivityWatch time tracking data, plus manage category configuration. Queries a running ActivityWatch server and returns formatted application usage duration and percentages for daily, weekly, or monthly periods. Automatically filters out AFK periods and uses local timezone.

**Features:**

- `activity` command (`a` alias) — daily, weekly, or monthly reports with category breakdown
- Pin reports to a specific date (`YYYY-MM-DD`) or month (`YYYY-MM`)
- Configurable top-N results (`--top`, default 10)
- Per-app activity timeline showing focus sessions and longest session
- Custom server URL support (`--url`, default `http://localhost:5600`)
- `category` command (`c` alias) — get/set ActivityWatch category rules with automatic backup
- `category unclassified` subcommand to find apps/titles not matched by any rule

### 🎵 lyrics-fetcher

Fetch song lyrics from Genius (https://genius.com) for a single song, an artist's catalog, or a full album, and print them as clean title + lyrics blocks. Wraps the `lyricsgenius` library and ships with section-header stripping, term exclusion, txt/json output, and optional file saving.

**Features:**

- Three subcommands: `song` (single track), `artist` (full catalog, multi-song), and `album` (full album, multi-song)
- Optional artist hint (`-a/--artist`) to avoid matching the wrong song with a shared title
- Section headers like `[Chorus]`/`[Verse]` stripped by default; keep them with `--keep-headers`
- Term exclusion (`--excluded-terms`) to skip remixes/live versions
- `txt` (default) or `json` output; `json` includes `title`, `artist`, `lyrics`, and `url`
- `--max-songs` cap for artists (default 10, `0` = all) with `title`/`popularity` sort and optional featured tracks
- `--save` writes results to the skill's `output/` directory with unsafe characters sanitized
- Non-song tracks (track listings, etc.) skipped automatically via `skip_non_songs`
- Requires a Genius `access_token` via `scripts/.env` (never committed)

## ⭐ Star History

<a href="https://www.star-history.com/?repos=techstay%2Fsome-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=techstay/some-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=techstay/some-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=techstay/some-skills&type=date&legend=top-left" />
 </picture>
</a>
