# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "cyclopts>=4.20.0",
#     "feedparser>=6.0.12",
#     "loguru>=0.7.0",
#     "pydantic>=2.0.0",
#     "selectolax>=0.3.0",
#     "whenever>=0.10.0",
# ]
# ///


import asyncio
import calendar
import enum
import json
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, cast

import feedparser
from cyclopts import App, Parameter, Token
from loguru import logger
from pydantic import BaseModel
from selectolax.parser import HTMLParser
from whenever import Instant, ZonedDateTime

# Default to INFO so debug logs stay quiet unless --debug is passed.
logger.remove()
logger.add(sys.stderr, level="INFO")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "cache"
NEWS_SOURCE_PATH = Path(__file__).resolve().parent.parent / "news-source.json"
OUTPUT_PATH = OUTPUT_DIR / "rss_output.json"


class Category(enum.Enum):
    """CLI-selectable news categories; values map to category names in news-source.json."""

    china = "China News"
    international = "International News"
    technology = "Technology"
    finance = "Business & Finance"
    politics = "Politics"
    sports = "Sports"
    science = "Science"
    health = "Health & Medicine"
    entertainment = "Entertainment"
    culture = "Culture & Education"


def _parse_categories(type_, tokens: Sequence[Token]) -> list[Category]:
    """Parse a comma-separated token like 'politics,technology' into a list of Categories."""
    result: list[Category] = []
    for part in tokens[0].value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            result.append(Category[part])  # match by name (e.g. "politics")
        except KeyError:
            try:
                result.append(Category(part))  # match by value (e.g. "Politics")
            except ValueError:
                valid = ", ".join(c.name for c in Category)
                raise ValueError(
                    f"Invalid category '{part}'. Valid choices: {valid}"
                ) from None
    return result


# Set a custom user agent to avoid being blocked by some RSS feeds.

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"

feedparser.USER_AGENT = USER_AGENT


class NewsItem(BaseModel):
    title: str
    link: str
    summary: str
    published: str


class FeedSource(BaseModel):
    display_name: str
    name: str
    url: str
    etag: str | None = None
    modified: str | None = None
    news: list[NewsItem] | None = None


class FeedCategory(BaseModel):
    category: str
    sources: list[FeedSource]


class FeedConfig(BaseModel):
    categories: list[FeedCategory]

    @classmethod
    def load(cls, path: Path = NEWS_SOURCE_PATH) -> "FeedConfig":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls.model_validate(raw)


class FeedOutput(BaseModel):
    last_sync: str
    article_count: int
    categories: dict[str, FeedCategory]


def fetch_news(source: FeedSource):
    """This function fetches news from a given RSS feed source and updates the source with the latest news items."""
    d = feedparser.parse(
        source.url,
        etag=source.etag,
        modified=source.modified,
    )

    if d.status == 304:
        logger.debug("No new news for source: {}", source.name)
        return

    if d.bozo:
        logger.warning("Feed parse warning for {}: {}", source.name, d.bozo_exception)

    source.etag = getattr(d, "etag", None)
    source.modified = getattr(d, "modified", None)

    news_items = []
    for item in d.entries:
        title = cast(str, item.title or "")
        link = cast(str, item.link)
        summary = cast(
            str,
            item.get("dc_content")
            or item.get("summary")
            or item.get("description")
            or "",
        )
        published_raw = cast(
            time.struct_time | None,
            item.get("published_parsed") or item.get("updated_parsed"),
        )

        published = (
            Instant.from_timestamp(calendar.timegm(published_raw)).format_iso()
            if published_raw
            else Instant.now().format_iso()
        )
        # Remove html tags
        summary = HTMLParser(summary).text(strip=True)

        news_items.append(
            NewsItem(
                title=title,
                link=link,
                summary=summary,
                published=published,
            )
        )

    source.news = news_items
    logger.debug("Fetched {} news items for source: {}", len(news_items), source.name)


def load_config() -> FeedConfig:
    """Load the feed configuration from the JSON file."""
    feed_config = FeedConfig.load()
    if OUTPUT_PATH.exists():
        cached_output = FeedOutput.model_validate_json(
            OUTPUT_PATH.read_text(encoding="utf-8")
        )
        for category in feed_config.categories:
            cached_category = cached_output.categories.get(category.category)
            if cached_category:
                for source in category.sources:
                    cached_source = next(
                        (s for s in cached_category.sources if s.name == source.name),
                        None,
                    )
                    if cached_source:
                        source.etag = cached_source.etag
                        source.modified = cached_source.modified
                        # Preserve cached news so a 304 response doesn't wipe it.
                        source.news = cached_source.news

    return feed_config


async def fetch_all_news():
    feed_config = load_config()

    all_sources: list[FeedSource] = []
    for category in feed_config.categories:
        all_sources.extend(category.sources)

    tasks = [asyncio.to_thread(fetch_news, source) for source in all_sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for source, result in zip(all_sources, results):
        if isinstance(result, Exception):
            logger.error("Failed to fetch news for source: {}\n{}", source.name, result)

    # Save to output
    output = FeedOutput(
        last_sync=ZonedDateTime.now("Asia/Shanghai").format_iso(),
        article_count=sum(len(source.news) for source in all_sources if source.news),
        categories={category.category: category for category in feed_config.categories},
    )
    OUTPUT_PATH.write_text(
        json.dumps(output.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.debug("Saved cache to {}", OUTPUT_PATH)


def to_yaml_like(obj, indent=0) -> str:
    """Render dict/list/str/int as YAML-like text."""
    prefix = " " * indent
    if isinstance(obj, dict):
        lines = []
        for key, value in obj.items():
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                nested = to_yaml_like(value, indent + 2)
                if nested:
                    lines.append(nested)
            else:
                lines.append(f"{prefix}{key}: {to_yaml_like(value, 0)}")
        return "\n".join(lines)
    elif isinstance(obj, list):
        lines = []
        for item in obj:
            if isinstance(item, dict):
                rendered = to_yaml_like(item, indent + 2)
                if rendered:
                    # Render dict inline: first key goes after "- ", rest stay indented
                    first_line, *rest_lines = rendered.split("\n")
                    marker = " " * (indent + 2)
                    if first_line.startswith(marker):
                        first_line = first_line[len(marker) :]
                    lines.append(f"{prefix}- {first_line}")
                    lines.extend(rest_lines)
                else:
                    lines.append(f"{prefix}- ")
            else:
                lines.append(f"{prefix}- {to_yaml_like(item, 0)}")
        return "\n".join(lines)
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    elif isinstance(obj, int):
        return str(obj)
    elif isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    elif obj is None:
        return ""
    return str(obj)


def should_refetch(refetch_interval_hours: int) -> bool:
    """Return True if the cache is missing or older than the refetch interval."""
    if not OUTPUT_PATH.exists():
        return True
    cached = FeedOutput.model_validate_json(OUTPUT_PATH.read_text(encoding="utf-8"))
    elapsed = Instant.now() - Instant.parse_iso(cached.last_sync)
    if elapsed.total("hours") < refetch_interval_hours:
        logger.debug(
            "Cache is fresh ({}h < {}h), skipping fetch.",
            elapsed.total("hours"),
            refetch_interval_hours,
        )
        return False
    return True


def build_display(enabled_categories: set[str], within_hours: int) -> dict:
    """Read the cache and build the display payload, filtered by category and time."""
    output = FeedOutput.model_validate_json(OUTPUT_PATH.read_text(encoding="utf-8"))

    now = Instant.now()
    display: dict[str, list[dict[str, str]]] = {}
    total_articles = 0
    for cat_name, cat in output.categories.items():
        if cat_name not in enabled_categories:
            continue
        articles: list[dict[str, str]] = []
        for source in cat.sources:
            if not source.news:
                continue
            for item in source.news:
                if within_hours > 0:
                    try:
                        item_instant = Instant.parse_iso(item.published)
                        if (now - item_instant).total("hours") > within_hours:
                            continue
                    except Exception:
                        logger.debug(
                            "Failed to parse published time, keeping item: {}",
                            item.published,
                        )
                articles.append({
                    "title": item.title,
                    "link": item.link,
                    "summary": item.summary,
                    "published": item.published,
                    "source": source.display_name,
                })
        display[cat_name] = articles
        total_articles += len(articles)

    return {
        "last_sync": output.last_sync,
        "article_count": total_articles,
        "categories": display,
    }


def render_summaries(display: dict) -> str:
    """Render only article summaries, one per block, separated by blank lines.

    Empty/whitespace-only summaries are skipped to avoid blank-line noise.
    This compact format is token-efficient for large-scale AI consumption.
    """
    blocks: list[str] = []
    for articles in display["categories"].values():
        for article in articles:
            summary = (article.get("summary") or "").strip()
            if not summary:
                continue
            blocks.append(summary)
    return "\n\n".join(blocks)


app = App(
    name="rss-fetch",
    help="Fetch news from RSS feeds and output compact summaries (blank-line separated).",
    help_flags=["--help", "-h"],
    version="1.0.0",
    default_parameter=Parameter(negative=(), show_default=False),
)


@app.default
async def main(
    *,
    categories: Annotated[
        list[Category] | None,
        Parameter(
            name=["--category", "-c"],
            n_tokens=1,
            converter=_parse_categories,
            help=(
                "Categories to fetch. Comma-separated, e.g. -c politics,technology. "
                "Defaults to all categories."
            ),
        ),
    ] = None,
    refetch_interval_hours: Annotated[
        int,
        Parameter(
            help="Skip fetch if cache is newer than this many hours.", show_default=True
        ),
    ] = 4,
    within_hours: Annotated[
        int,
        Parameter(
            help="Only show news published within this many hours. Use 0 to show all.",
            show_default=True,
        ),
    ] = 24,
    debug: Annotated[
        bool,
        Parameter(
            name=["--debug"],
            help="Enable debug-level logging.",
        ),
    ] = False,
    yaml: Annotated[
        bool,
        Parameter(
            name=["--yaml"],
            help=(
                "Output full structured YAML (title/link/summary/published/source). "
                "Default is compact summary-only output for AI consumption."
            ),
        ),
    ] = False,
):
    if debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    # Selected categories (defaults to all); values are news-source.json category names.
    enabled_categories: set[str] = (
        {c.value for c in categories} if categories else {c.value for c in Category}
    )

    if not enabled_categories:
        logger.warning("No categories enabled, nothing to fetch.")
        return

    if should_refetch(refetch_interval_hours):
        await fetch_all_news()

    result = build_display(enabled_categories, within_hours)
    if yaml:
        print(to_yaml_like(result))
    else:
        print(render_summaries(result))


if __name__ == "__main__":
    app()
