# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "cyclopts>=4.11.1",
#     "httpx>=0.28.1",
#     "python-dotenv>=1.2.2",
# ]
# ///

"""
TMDB metadata lookup helper for Jellyfin renaming.

Usage:
    uv run tmdb.py "Movie or Show Title"
    uv run tmdb.py "Movie or Show Title" --lang en-US --limit 5 --pretty
    uv run tmdb.py --help
"""

import json
import os
from dataclasses import asdict, dataclass
from typing import Annotated, Literal

import httpx
from cyclopts import App, Parameter, validators
from dotenv import load_dotenv

load_dotenv()

app = App(
    help="Search TMDB for movie and TV show metadata used when renaming Jellyfin media.",
    help_flags=["-h", "--help"],
    version_flags=["-v", "--version"],
    version="1.0.0",
)


@dataclass
class TMDBResult:
    id: int
    title: str
    original_title: str
    overview: str
    release_date: str
    media_type: str
    vote_average: float
    poster_path: str


def tmdb_result_from_raw(result: dict) -> TMDBResult:
    return TMDBResult(
        id=result["id"],
        title=result.get("title") or result.get("name") or "",
        original_title=result.get("original_title") or result.get("original_name") or "",
        overview=result.get("overview") or "",
        release_date=result.get("release_date") or result.get("first_air_date") or "",
        media_type=result.get("media_type") or "",
        vote_average=result.get("vote_average") or 0.0,
        poster_path=result.get("poster_path") or "",
    )


def tmdb_query(
    query: str, lang: Literal["en-US", "zh-CN", "ja-JP"] = "zh-CN"
) -> list[dict]:
    api_key = os.getenv("TMDB_API_KEY", "")
    if not api_key:
        raise ValueError("TMDB_API_KEY not found in environment variables.")

    base_url = "https://api.themoviedb.org/3/search/multi"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    params = {"query": query, "language": lang}

    response = httpx.get(base_url, headers=headers, params=params)
    results = []
    for result in response.json().get("results", []):
        results.append(tmdb_result_from_raw(result))
    return [asdict(result) for result in results]


@app.default
def cli(
    query: Annotated[str, Parameter(help="Movie or TV show title to search.")],
    lang: Annotated[
        Literal["en-US", "zh-CN", "ja-JP"],
        Parameter(name="--lang", help="TMDB response language."),
    ] = "zh-CN",
    limit: Annotated[
        int,
        Parameter(
            name="--limit",
            help="Maximum number of results to print.",
            validator=validators.Number(gte=1, lte=20),
        ),
    ] = 10,
    pretty: Annotated[
        bool, Parameter(name="--pretty", help="Pretty-print JSON output.")
    ] = False,
) -> bool:
    """Search TMDB and print JSON results."""
    try:
        data = tmdb_query(query, lang=lang)[:limit]
        print(json.dumps(data, ensure_ascii=False, indent=2 if pretty else None))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    app()
