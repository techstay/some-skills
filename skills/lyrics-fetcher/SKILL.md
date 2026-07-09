---
name: lyrics-fetcher
description: >
  Fetch song lyrics from Genius (https://genius.com). Search a single song,
  an artist's catalog, or a full album, and print lyrics as title + lyrics
  blocks. Use when the user asks for lyrics, song words, fetch/search a song's
  lyrics, get all lyrics by an artist, or pull an album's lyrics. The script
  wraps the `lyricsgenius` library and ships with section-header stripping,
  term exclusion, txt/json output, and optional file saving.
license: MIT
version: "1.0.0"
---

# Lyrics Fetcher

Fetches lyrics from Genius via the `lyricsgenius` library. Each subcommand searches Genius and prints lyrics as a **title + lyrics block**, with a trailing total count for multi-song results.

## Setup

Requires a Genius access token:

1. Register a free account at <https://genius.com/api-clients> and create a client to obtain an `access_token`.
2. Copy `scripts/.env.example` to `scripts/.env`.
3. Fill in `GENIUS_ACCESS_TOKEN`.
4. `.env` is gitignored and never committed.

The `lyricsgenius` library also reads `GENIUS_ACCESS_TOKEN` from the environment directly, but this script loads `.env` first and passes the token explicitly so a missing token produces a clear error.

## Quick Reference

```bash
cd skills/lyrics-fetcher/scripts

# Single song (artist optional but recommended for accuracy)
uv run lyrics_fetch.py song "Bohemian Rhapsody" "Queen"
uv run lyrics_fetch.py song "To You" -a "Andy Shauf"

# Artist - fetch up to N songs with lyrics
uv run lyrics_fetch.py artist "The Beatles" --max-songs 5
uv run lyrics_fetch.py artist "The Beatles" --max-songs 5 --include-features
uv run lyrics_fetch.py artist "The Beatles" --max-songs 0          # 0 = all songs

# Album
uv run lyrics_fetch.py album "The Party" -a "Andy Shauf"

# Keep [Chorus]-style section headers (stripped by default)
uv run lyrics_fetch.py song "Check the Rhyme" "A Tribe Called Quest" --keep-headers

# Output as JSON instead of plain text
uv run lyrics_fetch.py song "Begin Again" "Andy Shauf" --format json

# Save the output to the output/ directory
uv run lyrics_fetch.py artist "The Beatles" --max-songs 5 --save
uv run lyrics_fetch.py song "To You" "Andy Shauf" -f json --save

# Exclude remixes / live versions
uv run lyrics_fetch.py artist "The Beatles" --excluded-terms "(Remix)" "(Live)"
```

---

## Subcommands

| Subcommand | Searches by | Multi-song | Example                                              |
| ---------- | ----------- | ---------- | --------------------------------------------------- |
| `song`     | Song title  | No         | `uv run lyrics_fetch.py song "Title" "Artist"`      |
| `artist`   | Artist name | Yes        | `uv run lyrics_fetch.py artist "Artist" --max-songs 5` |
| `album`    | Album title | Yes        | `uv run lyrics_fetch.py album "Album" -a "Artist"`  |

---

## Command Options

| Option                | Applies to         | Default  | Description                                                                 |
| --------------------- | ------------------ | -------- | --------------------------------------------------------------------------- |
| `-a, --artist`        | `song`, `album`    | —        | Artist name. Optional but improves match accuracy.                          |
| `--max-songs`         | `artist`           | `10`     | Maximum songs to fetch. `0` means all songs (can be slow).                  |
| `--sort`              | `artist`           | `title`  | Sort order: `title` or `popularity`.                                        |
| `--include-features`  | `artist`           | Off      | Include songs where the artist is featured, not the primary artist.         |
| `--keep-headers`      | all                | Off      | Keep `[Chorus]`-style section headers (removed by default).                 |
| `--excluded-terms`    | all                | —        | Skip songs whose titles contain any of these terms, e.g. `(Remix)` `(Live)`.|
| `-f, --format`        | all                | `txt`    | Output format: `txt` or `json`.                                             |
| `--save`              | all                | Off      | Save output to `output/<safe-name>.<format>`.                               |
| `-h, --help`          | —                  | —        | Show help.                                                                  |
| `-v, --version`       | —                  | —        | Show version.                                                               |

For `song`, the title is the first positional argument and the artist is the `--artist` option. For `album`, the title is positional and the artist is `--artist`. For `artist`, the name is the single positional argument.

---

## Key Rules

| Rule                                       | Description                                                                                          |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| `--artist` improves accuracy               | Passing the artist narrows the search and avoids matching the wrong song with the same title.       |
| Section headers are stripped by default    | `[Chorus]`, `[Verse]`, etc. are removed unless `--keep-headers` is passed.                           |
| `--max-songs 0` means all songs            | Fetching every song by a prolific artist can be slow and hit rate limits; default is 10.             |
| Read `status` from stdout                  | On success the lyrics are printed; on failure `loguru` writes the error to stderr and the script exits non-zero. |
| Use `--format json` for structured output  | JSON includes `title`, `artist`, `lyrics`, and `url` (when available) for each song.                |
| `--save` writes to the skill's `output/`   | Files are named from the song/artist/album title with unsafe characters replaced by `_`.            |
| Non-song tracks are skipped automatically  | The client sets `skip_non_songs = True`, so track listings and other non-lyric content are dropped. |

---

## Output Format

For a single song (`txt`), the first line is the `Title - Artist` header followed by a blank line and the lyrics:

```
Bohemian Rhapsody - Queen

Is this the real life?
Is this just fantasy?
...
```

For multiple songs (`artist` / `album`), each song is a `Title - Artist` header followed by its lyrics, blocks separated by a single blank line, with a trailing total count:

```
Song One - The Beatles
<lyrics>

Song Two - The Beatles
<lyrics>

total 2 songs
```

When no song is found, the script prints `no song found` (or `no artist found` / `no album found`).

With `--format json`, a single song prints an object:

```json
{
  "title": "To You",
  "artist": "Andy Shauf",
  "lyrics "...",
  "url": "https://genius.com/..."
}
```

An artist or album prints an object with a `songs` array:

```json
{
  "name": "The Beatles",
  "songs": [
    { "title": "...", "artist": "...", "lyrics": "..." }
  ]
}
```

---

## Caching & Rate Limits

This script does not cache results — every invocation hits the Genius API. Genius rate-limits requests; fetching an artist's full catalog (`--max-songs 0`) may take a while. The client uses a small sleep between requests to stay polite. If you need to reuse results, pass `--save` and read the saved file instead of re-running.
