# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "cyclopts>=4.20.0",
#     "lyricsgenius>=3.11",
#     "loguru>=0.7.0",
#     "python-dotenv>=1.2.2",
# ]
# ///

"""Fetch song lyrics from Genius (https://genius.com) via the lyricsgenius library.

Subcommands:
  song    - search and print lyrics for a single song
  artist  - fetch songs (with lyrics) for an artist
  album   - fetch tracks (with lyrics) for an album

Requires a Genius access token. Set it in scripts/.env as GENIUS_ACCESS_TOKEN
or export it in your environment. Get one at https://genius.com/api-clients.
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Annotated, Literal

import lyricsgenius
from cyclopts import App, Parameter
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Log at INFO level to stderr; stdout is reserved for command output.
logger.remove()
logger.add(sys.stderr, level="INFO")

# Suppress the lyricsgenius library's chatty INFO/DEBUG logging.
logging.getLogger("lyricsgenius").setLevel(logging.WARNING)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def _get_token() -> str:
    """Read the Genius access token from the environment, exiting with a clear error if missing."""
    token = os.getenv("GENIUS_ACCESS_TOKEN")
    if not token:
        logger.error(
            "GENIUS_ACCESS_TOKEN is not set. Get one from "
            "https://genius.com/api-clients and put it in scripts/.env"
        )
        sys.exit(2)
    return token


def _make_genius(
    *, remove_headers: bool, excluded_terms: list[str]
) -> lyricsgenius.Genius:
    """Build a configured Genius client."""
    genius = lyricsgenius.Genius(_get_token(), timeout=20, retries=2, sleep_time=0.5)
    genius.remove_section_headers = remove_headers
    genius.skip_non_songs = True
    if excluded_terms:
        genius.excluded_terms = excluded_terms
    return genius


def _clean(text: str) -> str:
    """Strip surrounding whitespace from lyrics text."""
    return (text or "").strip()


def _song_record(song) -> dict:
    """Extract a plain dict from a lyricsgenius Song-like object (defensive)."""
    title = getattr(song, "title", "") or ""
    artist = getattr(song, "artist", "") or ""
    lyrics = _clean(getattr(song, "lyrics", ""))
    url = getattr(song, "url", "") or ""
    record = {"title": title, "artist": artist, "lyrics": lyrics}
    if url:
        record["url"] = url
    return record


def _render_song(record: dict) -> str:
    """Render a single song as 'Title - Artist' header followed by the lyrics."""
    title = record.get("title", "").strip()
    artist = record.get("artist", "").strip()
    lyrics = record.get("lyrics", "").strip()
    header = f"{title} - {artist}" if artist else title or "(unknown title)"
    body = lyrics if lyrics else "(lyrics not found)"
    return f"{header}\n\n{body}"


def _render_many(records: list[dict]) -> str:
    """Render multiple songs separated by blank lines with a trailing total count."""
    if not records:
        return "no songs found"
    blocks = [_render_song(r) for r in records]
    return "\n\n".join(blocks) + f"\n\ntotal {len(records)} songs"


def _safe_filename(name: str) -> str:
    """Turn an arbitrary name into a filesystem-safe stem."""
    stem = re.sub(r"[^\w\-]+", "_", name).strip("_")
    return stem or "output"


def _emit(
    payload: str | dict | list,
    *,
    fmt: str,
    save_name: str | None,
) -> None:
    """Print payload to stdout, optionally saving to the output/ directory."""
    if isinstance(payload, (dict, list)):
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        text = payload

    print(text)

    if save_name:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / f"{_safe_filename(save_name)}.{fmt}"
        path.write_text(text, encoding="utf-8")
        logger.info("Saved to {}", path)


app = App(
    name="lyrics-fetch",
    help="Fetch song lyrics from Genius. Subcommands: song, artist, album.",
    help_flags=["-h", "--help"],
    version_flags=["-v", "--version"],
    version="1.0.0",
    default_parameter=Parameter(negative=(), show_default=False),
)


@app.command(name="song", help="Search and print lyrics for a single song.")
def song(
    title: Annotated[str, Parameter(help="Song title to search for.")],
    artist: Annotated[
        str | None,
        Parameter(
            name=["--artist", "-a"],
            help="Artist name. Optional but improves match accuracy.",
        ),
    ] = None,
    keep_headers: Annotated[
        bool,
        Parameter(
            name="--keep-headers",
            help="Keep [Chorus]-style section headers in the lyrics (removed by default).",
        ),
    ] = False,
    excluded_terms: Annotated[
        list[str],
        Parameter(
            name="--excluded-terms",
            help="Skip songs whose titles contain any of these terms, e.g. '(Remix)' '(Live)'.",
        ),
    ] = [],
    fmt: Annotated[
        Literal["txt", "json"],
        Parameter(
            name=["--format", "-f"],
            help="Output format: txt (default) or json.",
        ),
    ] = "txt",
    save: Annotated[
        bool,
        Parameter(
            name="--save",
            help="Save output to output/ directory as <name>.<format>.",
        ),
    ] = False,
) -> None:
    genius = _make_genius(remove_headers=not keep_headers, excluded_terms=excluded_terms)
    try:
        result = genius.search_song(title, artist or "")
    except Exception as e:  # noqa: BLE001 - surface any library/HTTP failure cleanly
        logger.error("Search failed: {}", e)
        sys.exit(1)

    if result is None:
        print("no song found")
        return

    record = _song_record(result)

    if fmt == "json":
        payload: str | dict | list = record
    else:
        payload = _render_song(record)

    save_name = f"{record['title']} - {record['artist']}" if save else None
    _emit(payload, fmt=fmt, save_name=save_name)


@app.command(name="artist", help="Fetch songs (with lyrics) for an artist.")
def artist(
    name: Annotated[str, Parameter(help="Artist name to search for.")],
    max_songs: Annotated[
        int,
        Parameter(
            name="--max-songs",
            help="Maximum number of songs to fetch. 0 means all songs (can be slow).",
            show_default=True,
        ),
    ] = 10,
    sort: Annotated[
        Literal["title", "popularity"],
        Parameter(
            name="--sort",
            help="Sort order: title (default) or popularity.",
        ),
    ] = "title",
    include_features: Annotated[
        bool,
        Parameter(
            name="--include-features",
            help="Include songs where the artist is featured (not the primary artist).",
        ),
    ] = False,
    keep_headers: Annotated[
        bool,
        Parameter(
            name="--keep-headers",
            help="Keep [Chorus]-style section headers in the lyrics (removed by default).",
        ),
    ] = False,
    excluded_terms: Annotated[
        list[str],
        Parameter(
            name="--excluded-terms",
            help="Skip songs whose titles contain any of these terms.",
        ),
    ] = [],
    fmt: Annotated[
        Literal["txt", "json"],
        Parameter(
            name=["--format", "-f"],
            help="Output format: txt (default) or json.",
        ),
    ] = "txt",
    save: Annotated[
        bool,
        Parameter(
            name="--save",
            help="Save output to output/ directory as <name>.<format>.",
        ),
    ] = False,
) -> None:
    genius = _make_genius(remove_headers=not keep_headers, excluded_terms=excluded_terms)
    limit = None if max_songs <= 0 else max_songs

    try:
        artist_obj = genius.search_artist(
            name,
            max_songs=limit,
            sort=sort,
            include_features=include_features,
            get_full_info=True,
        )
    except Exception as e:  # noqa: BLE001
        logger.error("Artist search failed: {}", e)
        sys.exit(1)

    if artist_obj is None:
        print("no artist found")
        return

    records = [_song_record(s) for s in (artist_obj.songs or [])]

    if fmt == "json":
        payload: str | dict | list = {
            "name": getattr(artist_obj, "name", name),
            "songs": records,
        }
    else:
        payload = _render_many(records)

    save_name = getattr(artist_obj, "name", name) if save else None
    _emit(payload, fmt=fmt, save_name=save_name)


@app.command(name="album", help="Fetch tracks (with lyrics) for an album.")
def album(
    title: Annotated[str, Parameter(help="Album title to search for.")],
    artist: Annotated[
        str | None,
        Parameter(
            name=["--artist", "-a"],
            help="Artist name. Optional but improves match accuracy.",
        ),
    ] = None,
    keep_headers: Annotated[
        bool,
        Parameter(
            name="--keep-headers",
            help="Keep [Chorus]-style section headers in the lyrics (removed by default).",
        ),
    ] = False,
    excluded_terms: Annotated[
        list[str],
        Parameter(
            name="--excluded-terms",
            help="Skip songs whose titles contain any of these terms.",
        ),
    ] = [],
    fmt: Annotated[
        Literal["txt", "json"],
        Parameter(
            name=["--format", "-f"],
            help="Output format: txt (default) or json.",
        ),
    ] = "txt",
    save: Annotated[
        bool,
        Parameter(
            name="--save",
            help="Save output to output/ directory as <name>.<format>.",
        ),
    ] = False,
) -> None:
    genius = _make_genius(remove_headers=not keep_headers, excluded_terms=excluded_terms)

    try:
        album_obj = genius.search_album(title, artist or "", get_full_info=True)
    except Exception as e:  # noqa: BLE001
        logger.error("Album search failed: {}", e)
        sys.exit(1)

    if album_obj is None:
        print("no album found")
        return

    records = []
    for track in (album_obj.tracks or []):
        song_obj = getattr(track, "song", None) or track
        records.append(_song_record(song_obj))

    album_title = getattr(album_obj, "name", title)
    album_artist = getattr(album_obj, "artist", artist or "")

    if fmt == "json":
        payload: str | dict | list = {
            "title": album_title,
            "artist": album_artist,
            "songs": records,
        }
    else:
        payload = _render_many(records)

    save_name = album_title if save else None
    _emit(payload, fmt=fmt, save_name=save_name)


if __name__ == "__main__":
    app()
