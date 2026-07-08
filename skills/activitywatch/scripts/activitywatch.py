# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aw-client>=0.5.15",
#     "cyclopts>=4.20.0",
#     "pydantic>=2.0.0",
# ]
# ///

"""ActivityWatch computer activity statistics and category management.

Usage:
    uv run scripts/activitywatch.py a --daily
    uv run scripts/activitywatch.py activity --weekly --top 5
    uv run scripts/activitywatch.py c get
    uv run scripts/activitywatch.py c get -f out.json
    uv run scripts/activitywatch.py c set -f c.json
    uv run scripts/activitywatch.py c set -f c.json --no-backup
    uv run scripts/activitywatch.py c unclassified
    uv run scripts/activitywatch.py c unclassified --weekly
"""

import json
import re
import socket
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, cast
from urllib.parse import urlparse

from aw_client import ActivityWatchClient
from cyclopts import App, Parameter, validators
from pydantic import BaseModel, ConfigDict

DEFAULT_AW_URL = "http://localhost:5600"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
DEFAULT_TOP = 20
DEFAULT_TOP_APPS_PER_CAT = 6
# Timeline: merge adjacent same-app events within this gap, only show
# segments at least this long, wrap lines at this width, and collapse apps
# with at least this many long segments into one approximate range.
DEFAULT_GAP_SECONDS = 180
DEFAULT_MIN_SEG_SECONDS = 600
TIMELINE_MAX_WIDTH = 120
TIMELINE_FREQUENT_THRESHOLD = 6


# --- Models ------------------------------------------------------------------


class CategoryRule(BaseModel):
    """A single classification rule matched against window app/title."""

    model_config = ConfigDict(extra="allow")

    type: str  # "regex" or "none"
    regex: str | None = None
    ignore_case: bool | None = None


class Category(BaseModel):
    """An ActivityWatch category entry from the 'classes' server setting."""

    model_config = ConfigDict(extra="allow")

    name: list[str]
    rule: CategoryRule
    id: int | None = None
    data: dict | None = None


# --- ActivityWatch client helpers --------------------------------------------


def make_client(url: str = DEFAULT_AW_URL) -> ActivityWatchClient:
    """Build an ActivityWatchClient from a full server URL like http://host:port."""
    parsed = urlparse(url)
    return ActivityWatchClient(
        "activitywatch-stats",
        host=parsed.hostname or "127.0.0.1",
        port=parsed.port or 5600,
        testing=False,
    )


def get_hostname() -> str:
    """Return the hostname used in watcher bucket IDs (mirrors aw-watcher)."""
    return socket.gethostname()


def query_events(
    client: ActivityWatchClient,
    start: datetime,
    end: datetime,
) -> list[dict]:
    """Query raw window events over [start, end], excluding AFK periods.

    Returns the AFK-filtered event list from ``aw-watcher-window``. Each event
    has ``timestamp`` (ISO UTC), ``duration`` (seconds) and ``data`` with
    ``app``/``title``. Used by both :func:`aggregate_app_usage` (summary) and
    :func:`render_timeline` (per-app segments) so only one server query is made.

    start/end should be tz-aware datetimes. A manual query string is used
    instead of aw_client.queries.canonicalEvents because the latter relies on
    find_bucket()/flood() which the rust aw-server rejects with HTTP 500.
    """
    host = get_hostname()
    bid_window = f"aw-watcher-window_{host}"
    bid_afk = f"aw-watcher-afk_{host}"

    query = (
        f'events = query_bucket("{bid_window}"); '
        f'not_afk = filter_keyvals(query_bucket("{bid_afk}"), "status", ["not-afk"]); '
        f"events = filter_period_intersect(events, not_afk); "
        f"RETURN = events;"
    )
    result = client.query(query, [(start, end)])

    if not result or not isinstance(result[0], list):
        return []
    return [e for e in result[0] if isinstance(e, dict)]


def aggregate_app_usage(events: list[dict]) -> dict[str, float]:
    """Aggregate raw events into ``{app: seconds}`` (total duration per app).

    The ``data.app`` value is used as-is (typically the process/exe name on
    Windows); a trailing ``.exe`` is stripped at render time, not here.
    """
    app_usage: dict[str, float] = defaultdict(float)
    for event in events:
        data = event.get("data") or {}
        app = data.get("app") or "Unknown"
        app_usage[app] += _safe_float(event.get("duration", 0))
    return dict(app_usage)


# --- Display-name cleanup ----------------------------------------------------


def _strip_exe_ext(name: str) -> str:
    """Drop a trailing ``.exe`` (case-insensitive) from a process name."""
    lower = name.lower()
    if lower.endswith(".exe"):
        return name[: -len(".exe")]
    return name


def _safe_float(value, default: float = 0.0) -> float:
    """Coerce ``value`` to float, returning ``default`` on non-numeric input.

    Guards against malformed ``duration`` values from the server (None, str,
    object) that would otherwise crash aggregation with TypeError/ValueError.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# --- Time period helpers -----------------------------------------------------


def _parse_hhmm(value: str) -> timedelta:
    """Parse an 'HH:MM' string into a timedelta; default to 0 on failure."""
    try:
        hours, minutes = (int(x) for x in str(value).split(":"))
    except (ValueError, AttributeError):
        return timedelta(0)
    return timedelta(hours=hours, minutes=minutes)


def _get_setting_or_none(client: ActivityWatchClient, key: str) -> Any:
    """Read a server setting, returning None if the key is missing (HTTP 404).

    Connection errors and other unexpected errors propagate to the caller so
    the command-level handler can surface a clean "server not running" message
    instead of silently falling back to defaults.

    Returns ``Any`` because ActivityWatch settings can store arbitrary JSON
    values (e.g. ``startOfDay`` is a string, ``classes`` is a list). The
    upstream ``aw_client.get_setting`` is annotated as ``-> dict`` which is
    inaccurate for scalar settings; ``Any`` reflects the real runtime shape.
    """
    try:
        return client.get_setting(key)
    except Exception as e:
        response = getattr(e, "response", None)
        if response is not None and getattr(response, "status_code", None) == 404:
            return None
        raise


def read_day_bounds(client: ActivityWatchClient) -> tuple[timedelta, bool]:
    """Read startOfDay (HH:MM) and startOfWeek ('Monday'/'Sunday') settings.

    Falls back to midnight / Monday if the server does not expose them (fresh
    install returns 404), so the script still works without configuration.
    """
    start_of_day = _parse_hhmm(_get_setting_or_none(client, "startOfDay") or "00:00")
    sow = str(_get_setting_or_none(client, "startOfWeek") or "Monday").lower()
    week_starts_monday = sow != "sunday"
    return start_of_day, week_starts_monday


def period_bounds(
    period: str,
    *,
    date: str | None = None,
    start_of_day: timedelta = timedelta(0),
    week_starts_monday: bool = True,
) -> tuple[datetime, datetime, str, str]:
    """Compute (start_local, end_local, start_label, end_label) for a period.

    period is one of 'daily', 'weekly', 'monthly'. Returns tz-aware local
    datetimes suitable for the AW query, plus 'YYYY-MM-DD HH:MM' labels for the
    report header. start/end respect the server's startOfDay and startOfWeek.

    If date is given, the period is pinned to a specific day (``YYYY-MM-DD`` for
    daily/weekly) or month (``YYYY-MM`` for monthly) instead of the current one.
    For the current day/week/month the end bound is ``now``; for past periods
    the end bound is the natural end of that period.
    """
    now = datetime.now().astimezone()
    label_fmt = "%Y-%m-%d %H:%M"

    if date is None:
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if period == "daily":
            start = midnight + start_of_day
            if start > now:
                start -= timedelta(days=1)
            end = now
        elif period == "weekly":
            weekday = midnight.weekday()  # Monday=0
            days_since = weekday if week_starts_monday else (weekday + 1) % 7
            week_midnight = midnight - timedelta(days=days_since)
            start = week_midnight + start_of_day
            if start > now:
                start -= timedelta(weeks=1)
            end = now
        elif period == "monthly":
            month_midnight = midnight.replace(day=1)
            start = month_midnight + start_of_day
            if start > now:
                # Roll back to the previous month's start.
                month_midnight = (month_midnight - timedelta(days=1)).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                start = month_midnight + start_of_day
            end = now
        else:
            raise ValueError(f"Unknown period: {period}. Use daily/weekly/monthly.")
        return start, end, start.strftime(label_fmt), end.strftime(label_fmt)

    # Pinned to a specific day/month. ``date`` is assumed pre-validated by the
    # caller (YYYY-MM-DD for daily/weekly, YYYY-MM for monthly).
    if period == "daily":
        target = datetime.strptime(date, "%Y-%m-%d").astimezone()
        start = target + start_of_day
        end = start + timedelta(days=1)
        if end > now:
            end = now
    elif period == "weekly":
        target = datetime.strptime(date, "%Y-%m-%d").astimezone()
        target_midnight = target.replace(hour=0, minute=0, second=0, microsecond=0)
        weekday = target_midnight.weekday()  # Monday=0
        days_since = weekday if week_starts_monday else (weekday + 1) % 7
        week_midnight = target_midnight - timedelta(days=days_since)
        start = week_midnight + start_of_day
        end = start + timedelta(days=7)
        if end > now:
            end = now
    elif period == "monthly":
        # strptime with "%Y-%m" yields day=1 at midnight.
        target = datetime.strptime(date, "%Y-%m").astimezone()
        start = target + start_of_day
        if target.month == 12:
            next_month = target.replace(year=target.year + 1, month=1)
        else:
            next_month = target.replace(month=target.month + 1)
        end = next_month + start_of_day
        if end > now:
            end = now
    else:
        raise ValueError(f"Unknown period: {period}. Use daily/weekly/monthly.")

    return start, end, start.strftime(label_fmt), end.strftime(label_fmt)


# --- Rendering ---------------------------------------------------------------


def format_duration(seconds: float) -> str:
    """Format seconds as a compact human-readable duration.

    Examples: '45s', '37m', '4h12m', '1d3h'.

    Seconds are shown only when the total is under an hour (e.g. '37m55s');
    once hours or days are present they are dropped for brevity (e.g. '4h12m'
    rather than '4h12m3s').
    """
    total = int(seconds)
    if total < 60:
        return f"{total}s"
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not days and not hours and secs:
        parts.append(f"{secs}s")
    return "".join(parts) or "0s"


def render_report(
    period: str,
    start_label: str,
    end_label: str,
    app_usage: dict[str, float],
    *,
    top: int = DEFAULT_TOP,
) -> str:
    """Render an activity report for the given period as plain text.

    Apps are aggregated by ``data.app`` (one entry per application, not per
    window/tab). The display name is the ``app`` value with a trailing
    ``.exe`` stripped (e.g. ``firefox.exe`` -> ``firefox``); no window-title
    reverse lookup is performed. Entries that resolve to the same name are
    merged so consolidated applications roll up together.

    ``start_label``/``end_label`` are the actual first/last activity
    timestamps (not the configured period bounds), so the Period line
    reflects when the user was really at the computer. The Active line
    reports the AFK-filtered active duration only - no wall-clock fraction,
    since the idle/sleep gap is already implied by the (often much wider)
    Period span.
    """
    title = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}[period]

    display_usage: dict[str, float] = defaultdict(float)
    for app, seconds in app_usage.items():
        display_usage[_strip_exe_ext(app)] += seconds

    total_seconds = sum(display_usage.values())
    total_apps = len(display_usage)
    sorted_apps = sorted(display_usage.items(), key=lambda x: x[1], reverse=True)[:top]

    lines = [f"{title} Activity Report", f"Period: {start_label} ~ {end_label}"]

    if not display_usage:
        lines.append("No activity recorded in this period.")
        return "\n".join(lines)

    lines.append(f"Active: {format_duration(total_seconds)}")
    lines.append(f"Top {len(sorted_apps)} applications:")
    name_w = max((len(app) for app, _ in sorted_apps), default=0)
    for app, seconds in sorted_apps:
        pct = (seconds / total_seconds * 100) if total_seconds > 0 else 0
        lines.append(f"  {app:<{name_w}} {format_duration(seconds)} ({pct:.1f}%)")

    suffix = ""
    if total_apps > top:
        shown_seconds = sum(s for _, s in sorted_apps)
        coverage = (shown_seconds / total_seconds * 100) if total_seconds > 0 else 0
        suffix = f" (top {top} shown, covers {coverage:.1f}%)"
    lines.append(
        f"Total: {format_duration(total_seconds)} across {total_apps} apps{suffix}"
    )
    return "\n".join(lines)


# --- Timeline (per-app segments) --------------------------------------------


def _parse_event_time(event: dict) -> datetime | None:
    """Parse an event's ISO-UTC ``timestamp`` into a local-aware datetime."""
    ts = event.get("timestamp")
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts)).astimezone()
    except ValueError:
        return None


def _coalesce_segments(
    events: list[dict], gap_seconds: float
) -> list[tuple[datetime, datetime, float]]:
    """Merge one app's events into (start, end, duration) segments.

    ``events`` must already be filtered to a single app and sorted by
    timestamp. Adjacent events whose gap (end of prev -> start of next) is
    <= ``gap_seconds`` are joined into one segment; otherwise a new segment
    starts. Returns local-aware datetimes.
    """
    segs: list[tuple[datetime, datetime, float]] = []
    for event in events:
        start = _parse_event_time(event)
        if start is None:
            continue
        dur = _safe_float(event.get("duration", 0))
        end = start + timedelta(seconds=dur)
        if segs and (start - segs[-1][1]) <= timedelta(seconds=gap_seconds):
            old_start, _, _ = segs[-1]
            segs[-1] = (old_start, end, (end - old_start).total_seconds())
        else:
            segs.append((start, end, dur))
    return segs


def _group_events_by_app(events: list[dict]) -> dict[str, list[dict]]:
    """Group raw events by ``data.app`` and sort each group by timestamp.

    Pre-grouping once turns per-app scans from O(n*m) into O(n) total across
    :func:`render_timeline` and :func:`compute_focus_stats`. Pre-sorting mirrors
    the server's chronological order so callers can feed
    :func:`_coalesce_segments` directly without re-sorting.
    """
    grouped: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        app = (e.get("data") or {}).get("app")
        if app:
            grouped[app].append(e)
    for app in grouped:
        grouped[app].sort(key=lambda e: str(e.get("timestamp", "")))
    return grouped


def _render_app_timeline_line(
    app: str,
    long_segs: list[tuple[datetime, datetime, float]],
    *,
    min_seg_min: int,
    max_width: int,
) -> str:
    """Render one app's timeline line.

    Segments (already longest-first) are listed until ``max_width`` is reached,
    then ``+N more``. Apps with ``TIMELINE_FREQUENT_THRESHOLD`` or more long
    segments collapse to one approximate range with a 'switched frequently'
    note.
    """
    name = _strip_exe_ext(app)
    prefix = f"  {name:<18} "

    if not long_segs:
        return f"{prefix}(no segments >= {min_seg_min}m)"

    if len(long_segs) >= TIMELINE_FREQUENT_THRESHOLD:
        start = min(s[0] for s in long_segs)
        end = max(s[1] for s in long_segs)
        total = sum(s[2] for s in long_segs)
        return (
            f"{prefix}{start:%H:%M}-{end:%H:%M} (~{format_duration(total)})  "
            "[switched frequently, approximate range only]"
        )

    seg_strs = [f"{s[0]:%H:%M}-{s[1]:%H:%M} {format_duration(s[2])}" for s in long_segs]
    parts: list[str] = []
    width = len(prefix)
    for i, seg in enumerate(seg_strs):
        addition = seg if not parts else "  " + seg
        remaining_after = len(seg_strs) - i - 1
        suffix = f"  +{remaining_after} more" if remaining_after > 0 else ""
        if parts and width + len(addition) + len(suffix) > max_width:
            break
        parts.append(addition)
        width += len(addition)
    line = prefix + "".join(parts)
    remaining = len(seg_strs) - len(parts)
    if remaining > 0:
        line += f"  +{remaining} more"
    return line


def render_timeline(
    app_events_map: dict[str, list[dict]],
    app_usage: dict[str, float],
    *,
    top: int,
    gap: float,
    min_seg: float,
    max_width: int = TIMELINE_MAX_WIDTH,
) -> str:
    """Render a per-app timeline of long activity segments.

    For each top app (by total duration), adjacent events within ``gap``
    seconds are merged; only segments >= ``min_seg`` seconds are shown,
    in chronological order (left-to-right reads as the day's flow). Lines
    wrap at ``max_width`` with a ``+N more`` tail, and frequently-switched
    apps collapse to one approximate range. Apps with no long segments are
    omitted; a trailing line reports how many were skipped.
    """
    if not app_usage:
        return ""

    top_apps = sorted(app_usage, key=lambda k: app_usage[k], reverse=True)[:top]
    gap_min = int(gap // 60)
    min_seg_min = int(min_seg // 60)
    header = f"Top apps timeline  (gap<={gap_min}m  segs>={min_seg_min}m  top{top})"

    lines = [header]
    skipped = 0
    for app in top_apps:
        segs = _coalesce_segments(app_events_map.get(app, []), gap)
        long_segs = sorted((s for s in segs if s[2] >= min_seg), key=lambda s: s[0])
        if not long_segs:
            skipped += 1
            continue
        lines.append(
            _render_app_timeline_line(
                app, long_segs, min_seg_min=min_seg_min, max_width=max_width
            )
        )
    if skipped:
        lines.append(
            f"({skipped} of {len(top_apps)} apps had no segments >= {min_seg_min}m)"
        )
    return "\n".join(lines)


def compute_focus_stats(
    app_events_map: dict[str, list[dict]],
    app_usage: dict[str, float],
    *,
    gap: float,
    min_seg: float,
) -> tuple[int, tuple[str, datetime, datetime, float] | None]:
    """Count long focus segments across all apps and find the longest one.

    A focus segment is a merged same-app run >= ``min_seg`` seconds (same
    threshold as the timeline). Returns ``(count, longest)`` where ``longest``
    is ``(display_app, start, end, seconds)`` or ``None`` if there are none.
    """
    count = 0
    longest: tuple[str, datetime, datetime, float] | None = None
    for app in app_usage:
        segs = _coalesce_segments(app_events_map.get(app, []), gap)
        for s in segs:
            if s[2] >= min_seg:
                count += 1
                if longest is None or s[2] > longest[3]:
                    longest = (_strip_exe_ext(app), s[0], s[1], s[2])
    return count, longest


# --- Daily routine (per-day first/last activity) -----------------------------


def aggregate_daily_routine(
    events: list[dict],
    start_of_day: timedelta,
) -> list[tuple[date, datetime, datetime, float]]:
    """Group events by 'routine day' and return per-day (first, last, active).

    A routine day is offset from the natural calendar day by ``start_of_day``
    (e.g. ``startOfDay=04:00`` means a 03:00 event belongs to the previous
    day's routine), mirroring the server's day-boundary semantics used by
    :func:`period_bounds`. Each event contributes both its start
    (``timestamp``) and its end (``timestamp + duration``) so the
    last-activity time reflects when the user actually stopped, not when the
    last event began. The returned ``active`` seconds is the AFK-filtered
    total (sum of event durations) for that routine day - the true time the
    user spent at the computer, excluding idle/away gaps, which the wall-clock
    start~end window alone would overstate.

    Days with no events are omitted; callers fill the calendar gaps.
    """
    buckets: dict[date, list[datetime]] = defaultdict(list)
    active_seconds: dict[date, float] = defaultdict(float)
    for event in events:
        start = _parse_event_time(event)
        if start is None:
            continue
        dur = _safe_float(event.get("duration", 0))
        end = start + timedelta(seconds=dur)
        routine_day = (start - start_of_day).date()
        buckets[routine_day].append(start)
        buckets[routine_day].append(end)
        active_seconds[routine_day] += dur

    return [
        (day, min(times), max(times), active_seconds[day])
        for day, times in sorted(buckets.items())
    ]


def render_routine_report(
    period: str,
    period_label: str,
    rows: list[tuple[date, datetime, datetime, float]],
    *,
    start_of_day: timedelta,
    now: datetime,
) -> str:
    """Render a per-day routine report, one line per day.

    ``rows`` must be sorted ascending by day. Calendar days inside the
    covered range that have no events are emitted as ``(no activity)`` so the
    output stays contiguous and gaps are visible. Each day line shows the
    earliest and latest AFK-filtered activity times, the ``active`` duration
    (AFK-filtered total, see :func:`aggregate_daily_routine`), and
    annotations: ``(+1d)`` when the last activity falls past midnight of the
    routine day (the user kept going into the next calendar day), and
    ``(in progress)`` on today's row since the day is not over yet.

    ``start_of_day`` is shown in the header so the reader knows how routine
    days were computed.
    """
    title = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}[period]
    sod_minutes = int(start_of_day.total_seconds() // 60)
    sod_str = f"{sod_minutes // 60:02d}:{sod_minutes % 60:02d}"

    lines = [
        f"{title} Routine",
        f"Period: {period_label}",
        f"Day starts at: {sod_str}",
        "",
    ]

    if not rows:
        lines.append("No activity recorded in this period.")
        return "\n".join(lines)

    by_day = {day: (first, last, active) for day, first, last, active in rows}
    first_day = min(by_day)
    last_day = max(by_day)
    today = now.date()

    cursor = first_day
    while cursor <= last_day:
        day_data = by_day.get(cursor)
        if day_data is None:
            lines.append(f"  {cursor}  (no activity)")
        else:
            first, last, active = day_data
            cross = " (+1d)" if last.date() > cursor else ""
            progress = "  (in progress)" if cursor == today else ""
            lines.append(
                f"  {cursor}  {first:%H:%M} ~ {last:%H:%M}{cross}{progress}"
                f"  active {format_duration(active)}"
            )
        cursor += timedelta(days=1)

    return "\n".join(lines)


# --- Category helpers --------------------------------------------------------


def get_categories(client: ActivityWatchClient) -> list[Category]:
    """Read the current category config from the 'classes' server setting."""
    raw = _get_setting_or_none(client, "classes")
    if not raw:
        return []
    items = raw if isinstance(raw, list) else []
    return [Category.model_validate(item) for item in items]


def categories_to_payload(categories: list[Category]) -> list[dict]:
    """Serialize categories to the JSON list shape stored under 'classes'.

    None fields are excluded so the output matches the server's native format
    (e.g. {"type": "none"} rules omit regex/ignore_case) and get -> file -> set
    -> get is a clean roundtrip.
    """
    return [c.model_dump(mode="json", exclude_none=True) for c in categories]


def write_categories(
    client: ActivityWatchClient,
    categories: list[Category],
    *,
    backup: bool = True,
) -> Path | None:
    """Write a new category config, optionally backing up the previous one.

    Returns the backup file path if a backup was written, else None. The backup
    is written atomically (temp file + rename) to survive partial writes.
    """
    backup_path: Path | None = None
    if backup:
        current = get_categories(client)
        if current:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_path = CACHE_DIR / f"categories-backup-{ts}.json"
            tmp_path = backup_path.with_suffix(".json.tmp")
            tmp_path.write_text(
                json.dumps(
                    categories_to_payload(current), indent=2, ensure_ascii=False
                ),
                encoding="utf-8",
            )
            tmp_path.replace(backup_path)

    # set_setting's upstream stub types `value` as str, but ActivityWatch
    # accepts any JSON-serializable value (here a list[dict]); cast to Any.
    client.set_setting("classes", cast(Any, categories_to_payload(categories)))
    return backup_path


def build_category_matchers(
    categories: list[Category],
) -> list[tuple[list[str], re.Pattern]]:
    """Compile each regex rule into ``(name_path, pattern)``.

    ``none`` rules are **skipped** - in ActivityWatch they match nothing; they
    only exist so a category can act as a parent folder for its children.
    Invalid regexes are skipped (the server would reject them too). Returned in
    category list order so ties are broken by later-in-list (deepest wins).
    """
    matchers: list[tuple[list[str], re.Pattern]] = []
    for cat in categories:
        rule = cat.rule
        if rule.type == "none" or not rule.regex:
            continue
        flags = re.IGNORECASE if rule.ignore_case else 0
        try:
            matchers.append((cat.name, re.compile(rule.regex, flags)))
        except re.error:
            continue
    return matchers


def classify_event(
    app: str, title: str, matchers: list[tuple[list[str], re.Pattern]]
) -> list[str]:
    """Return the deepest matching category name path, or ``["Uncategorized"]``.

    Mirrors ActivityWatch's ``categorize``: every regex rule is tested against
    the app name *or* the window title (substring search); among the matches
    the one with the longest ``name`` path wins, with ties broken by
    later-in-list. An event matching no rule lands in ``["Uncategorized"]``.
    """
    best: list[str] | None = None
    for name, pat in matchers:
        if pat.search(app) or pat.search(title):
            if best is None or len(name) >= len(best):
                best = name
    return best if best is not None else ["Uncategorized"]


def render_category_breakdown(
    events: list[dict],
    categories: list[Category],
    *,
    total_seconds: float,
    top_apps_per_cat: int = DEFAULT_TOP_APPS_PER_CAT,
) -> str:
    """Render a top-level category rollup. Empty string if no categories.

    Each event is classified with AW semantics (deepest matching regex wins,
    else ``Uncategorized``) and rolled up to the first element of its category
    path. Rows are sorted by duration descending; each row lists the top
    contributing apps. Matching uses the raw ``app`` name; display strips a
    trailing ``.exe``.
    """
    if not categories:
        return ""

    matchers = build_category_matchers(categories)
    cat_apps: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for event in events:
        data = event.get("data") or {}
        raw_app = str(data.get("app") or "")
        title = str(data.get("title") or "")
        name_path = classify_event(raw_app, title, matchers)
        top = name_path[0] if name_path else "Uncategorized"
        display_app = _strip_exe_ext(raw_app) or "Unknown"
        cat_apps[top][display_app] += _safe_float(event.get("duration", 0))

    rows: list[tuple[str, float, list[str]]] = []
    for top, apps in cat_apps.items():
        seconds = sum(apps.values())
        names = [
            a
            for a, _ in sorted(apps.items(), key=lambda x: x[1], reverse=True)[
                :top_apps_per_cat
            ]
        ]
        rows.append((top, seconds, names))
    rows.sort(key=lambda r: r[1], reverse=True)

    name_w = min(max((len(r[0]) for r in rows), default=0), 24)
    lines = ["Category breakdown:"]
    for name, seconds, names in rows:
        pct = (seconds / total_seconds * 100) if total_seconds > 0 else 0
        lines.append(
            f"  {name:<{name_w}}  {format_duration(seconds)} ({pct:.1f}%)  "
            f"- {', '.join(names)}"
        )
    return "\n".join(lines)


# --- CLI ---------------------------------------------------------------------


def _format_client_error(url: str, exc: Exception) -> str:
    """Format a client error, distinguishing 'server not reachable' from 'server error'.

    A connection failure (no HTTP response attached) suggests the server is not
    running, so the user is told to start it. An HTTP error (e.g. 500) means the
    server is up but the request failed, so we report the status code instead of
    the misleading 'ensure server is running' hint.
    """
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None) if response is not None else None
    if status is not None:
        return f"Error: ActivityWatch server at {url} returned HTTP {status}: {exc}"
    return f"Error: {exc}\nPlease ensure ActivityWatch server is running (tried: {url})"


def _err(msg: str) -> None:
    """Print an error message to stderr (keeps stdout clean for data)."""
    print(msg, file=sys.stderr)


def _resolve_period(
    daily: bool, weekly: bool, monthly: bool, date: str | None
) -> tuple[str, str | None] | None:
    """Validate period flags + date and return ``(period, date)`` or ``None``.

    Shared by ``activity`` and ``category unclassified``. Ensures at most one
    of ``--daily``/``--weekly``/``--monthly`` is set (defaulting to ``daily``)
    and that ``date`` matches the expected format for the chosen period
    (``YYYY-MM-DD`` for daily/weekly, ``YYYY-MM`` for monthly). On error the
    message is printed to stderr and ``None`` is returned so the caller can
    bail out.
    """
    selected = [
        p
        for p, flag in (("daily", daily), ("weekly", weekly), ("monthly", monthly))
        if flag
    ]
    if len(selected) > 1:
        _err(
            f"Error: only one of --daily/--weekly/--monthly can be set, "
            f"got: {', '.join(selected)}"
        )
        return None
    period = selected[0] if selected else "daily"

    if date is not None:
        if period == "monthly":
            try:
                datetime.strptime(date, "%Y-%m")
            except ValueError:
                _err(f"Error: invalid month '{date}', expected YYYY-MM (e.g. 2025-07).")
                return None
        else:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                _err(
                    f"Error: invalid date '{date}', expected "
                    f"YYYY-MM-DD (e.g. 2015-02-27)."
                )
                return None
    return period, date


def _fetch_period_data(
    url: str, period: str, date: str | None
) -> tuple[list[dict], list[Category], str, str] | None:
    """Fetch events and categories for a period.

    Shared by ``activity`` and ``category unclassified``. Builds the client,
    resolves period bounds (respecting the server's startOfDay/startOfWeek),
    queries AFK-filtered events, and reads the current categories. Returns
    ``(events, categories, start_label, end_label)`` on success, or ``None``
    (with the error already printed to stderr) on connection/server failure
    so the caller can bail out cleanly.
    """
    try:
        client = make_client(url)
        start_of_day, week_starts_monday = read_day_bounds(client)
        start, end, start_label, end_label = period_bounds(
            period,
            date=date,
            start_of_day=start_of_day,
            week_starts_monday=week_starts_monday,
        )
        events = query_events(client, start, end)
        categories = get_categories(client)
    except (ConnectionError, OSError) as e:
        _err(_format_client_error(url, e))
        return None
    return events, categories, start_label, end_label


def _render_routine(url: str, period: str, date: str | None) -> None:
    """Fetch events for the period and print a per-day routine report.

    Dedicated path for ``--routine``: builds the client, resolves period
    bounds (respecting ``startOfDay``/``startOfWeek``), queries AFK-filtered
    events, aggregates per-day first/last activity, and prints the report.
    Kept separate from :func:`_fetch_period_data` because routine needs
    ``start_of_day`` (other callers do not) and does not need categories.
    """
    try:
        client = make_client(url)
        start_of_day, week_starts_monday = read_day_bounds(client)
        start, end, start_label, end_label = period_bounds(
            period,
            date=date,
            start_of_day=start_of_day,
            week_starts_monday=week_starts_monday,
        )
        events = query_events(client, start, end)
    except (ConnectionError, OSError) as e:
        _err(_format_client_error(url, e))
        return

    rows = aggregate_daily_routine(events, start_of_day)
    period_label = date or f"{start:%Y-%m-%d} ~ {end:%Y-%m-%d}"
    print(
        render_routine_report(
            period,
            period_label,
            rows,
            start_of_day=start_of_day,
            now=datetime.now().astimezone(),
        )
    )


DateArg = Annotated[
    str | None,
    Parameter(
        help=(
            "Optional date to pin the period to. "
            "YYYY-MM-DD for --daily/--weekly (e.g. 2015-02-27), "
            "YYYY-MM for --monthly (e.g. 2025-07). "
            "Defaults to the current day/week/month."
        ),
    ),
]
UrlArg = Annotated[str, Parameter(name="--url", help="ActivityWatch server URL.")]


app = App(
    name="activitywatch",
    help="ActivityWatch computer activity statistics and category management.",
    help_flags=["-h", "--help"],
    version="1.0.0",
    default_parameter=Parameter(negative=(), show_default=False),
)

activity_app = App(name="activity", help="Show activity reports.")
category_app = App(name="category", help="Get, set, or inspect category configuration.")


@activity_app.default
def activity_cmd(
    date: DateArg = None,
    *,
    daily: Annotated[
        bool, Parameter(name="--daily", help="Show today's activity (default).")
    ] = False,
    weekly: Annotated[
        bool, Parameter(name="--weekly", help="Show this week's activity.")
    ] = False,
    monthly: Annotated[
        bool, Parameter(name="--monthly", help="Show this month's activity.")
    ] = False,
    routine: Annotated[
        bool,
        Parameter(
            name="--routine",
            help=(
                "Show per-day first/last activity times (sleep/routine view). "
                "Best with --weekly or --monthly."
            ),
        ),
    ] = False,
    top: Annotated[
        int,
        Parameter(
            name="--top",
            help="Number of top applications to list.",
            validator=validators.Number(gte=1, lte=100),
        ),
    ] = DEFAULT_TOP,
    url: UrlArg = DEFAULT_AW_URL,
) -> None:
    """Show daily, weekly, or monthly computer activity (default: daily).

    An optional positional ``date`` pins the report to a specific day
    (``YYYY-MM-DD`` for daily/weekly) or month (``YYYY-MM`` for monthly).
    """
    resolved = _resolve_period(daily, weekly, monthly, date)
    if resolved is None:
        return
    period, date = resolved

    if routine:
        if period == "daily":
            _err(
                "Error: --routine needs --weekly or --monthly "
                "(a single day has no per-day breakdown)."
            )
            return
        _render_routine(url, period, date)
        return

    fetched = _fetch_period_data(url, period, date)
    if fetched is None:
        return
    events, categories, start_label, end_label = fetched

    # Report the actual activity window (first..last event) rather than the
    # configured period bounds, which include pre-wakeup / sleep hours that
    # are not informative for an activity report.
    event_times = [t for t in (_parse_event_time(e) for e in events) if t is not None]
    if event_times:
        label_fmt = "%Y-%m-%d %H:%M"
        start_label = min(event_times).strftime(label_fmt)
        end_label = max(event_times).strftime(label_fmt)

    app_usage = aggregate_app_usage(events)
    total_seconds = sum(app_usage.values())
    app_events_map = _group_events_by_app(events)
    print(render_report(period, start_label, end_label, app_usage, top=top))

    cat_block = render_category_breakdown(
        events, categories, total_seconds=total_seconds
    )
    if cat_block:
        print()
        print(cat_block)

    print()
    print(
        render_timeline(
            app_events_map,
            app_usage,
            top=top,
            gap=DEFAULT_GAP_SECONDS,
            min_seg=DEFAULT_MIN_SEG_SECONDS,
        )
    )

    min_seg_min = int(DEFAULT_MIN_SEG_SECONDS // 60)
    count, longest = compute_focus_stats(
        app_events_map,
        app_usage,
        gap=DEFAULT_GAP_SECONDS,
        min_seg=DEFAULT_MIN_SEG_SECONDS,
    )
    if longest is None:
        focus_line = f"Focus sessions (>={min_seg_min}m): 0"
    else:
        name, st, en, dur = longest
        focus_line = (
            f"Focus sessions (>={min_seg_min}m): {count}  |  "
            f"Longest: {format_duration(dur)} ({name} {st:%H:%M}-{en:%H:%M})"
        )
    print(focus_line)


@category_app.command(name="get")
def category_get(
    *,
    file: Annotated[
        Path | None,
        Parameter(
            name=["--file", "-f"],
            help="Write categories to this file instead of stdout.",
        ),
    ] = None,
    url: UrlArg = DEFAULT_AW_URL,
) -> None:
    """Read the current ActivityWatch category configuration."""
    try:
        client = make_client(url)
        categories = get_categories(client)
    except (ConnectionError, OSError) as e:
        _err(_format_client_error(url, e))
        return

    payload = categories_to_payload(categories)
    if file is not None:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Wrote {len(categories)} categories to {file}")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))


@category_app.command(name="set")
def category_set(
    *,
    file: Annotated[
        Path,
        Parameter(
            name=["--file", "-f"],
            help="JSON file with the new category config.",
        ),
    ],
    no_backup: Annotated[
        bool,
        Parameter(
            name="--no-backup",
            help="Skip backing up the current config before overwriting.",
        ),
    ] = False,
    url: UrlArg = DEFAULT_AW_URL,
) -> None:
    """Set the ActivityWatch category configuration from a JSON file.

    The previous configuration is backed up to cache/ by default; pass
    --no-backup to skip.
    """
    if not file.is_file():
        _err(f"Error: category config file not found: {file}")
        return

    try:
        raw = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _err(f"Error: invalid JSON in {file}: {e}")
        return
    if not isinstance(raw, list):
        _err("Error: category config must be a JSON array of category objects.")
        return
    try:
        categories = [Category.model_validate(item) for item in raw]
    except Exception as e:  # noqa: BLE001 - surface validation errors cleanly
        _err(f"Error: invalid category entry: {e}")
        return

    try:
        client = make_client(url)
        backup_path = write_categories(client, categories, backup=not no_backup)
    except (ConnectionError, OSError) as e:
        _err(_format_client_error(url, e))
        return

    if backup_path is not None:
        print(f"Backed up previous categories to {backup_path}")
    print(f"Updated categories: {len(categories)} rules written.")


@category_app.command(name="unclassified")
def category_unclassified(
    date: DateArg = None,
    *,
    daily: Annotated[
        bool, Parameter(name="--daily", help="Scan today's activity (default).")
    ] = False,
    weekly: Annotated[
        bool, Parameter(name="--weekly", help="Scan this week's activity.")
    ] = False,
    monthly: Annotated[
        bool, Parameter(name="--monthly", help="Scan this month's activity.")
    ] = False,
    url: UrlArg = DEFAULT_AW_URL,
) -> None:
    """List app names and window titles not matched by any category rule.

    Scans activity events in the given period and reports apps/titles that no
    ``regex`` category rule matches — i.e. entries that fall through to the
    ``Uncategorized`` catch-all. Use this to discover what new categories to
    add, then use ``c get`` / ``c set`` to update the config.
    """
    resolved = _resolve_period(daily, weekly, monthly, date)
    if resolved is None:
        return
    period, date = resolved

    fetched = _fetch_period_data(url, period, date)
    if fetched is None:
        return
    events, categories, start_label, end_label = fetched

    matchers = build_category_matchers(categories)

    # Map each uncategorized app to the set of its uncategorized window titles.
    # App names are cleaned (.exe stripped) for display; matching uses the raw
    # app name to mirror ActivityWatch's behavior.
    unclassified: dict[str, set[str]] = {}
    for event in events:
        data = event.get("data") or {}
        app = str(data.get("app") or "")
        title = str(data.get("title") or "")
        if app and not any(pat.search(app) or pat.search(title) for _, pat in matchers):
            display_app = _strip_exe_ext(app)
            titles = unclassified.setdefault(display_app, set())
            if title:
                titles.add(title)

    lines = [
        "Uncategorized apps and titles",
        f"Period: {start_label} ~ {end_label}",
    ]
    if not unclassified:
        lines.append("All activity matched by existing category rules.")
        print("\n".join(lines))
        return

    # One line per app: "app  -  title1, title2, title3, ..."
    # Show at most 3 sample titles; append ", ..." when truncated.
    max_titles = 3
    for app in sorted(unclassified):
        title_list = sorted(unclassified[app])
        if len(title_list) > max_titles:
            title_str = ", ".join(title_list[:max_titles]) + ", ..."
        elif title_list:
            title_str = ", ".join(title_list)
        else:
            title_str = ""
        if title_str:
            lines.append(f"  {app}  -  {title_str}")
        else:
            lines.append(f"  {app}")

    print("\n".join(lines))


app.command(activity_app, name=["activity", "a"])
app.command(category_app, name=["category", "c"])


if __name__ == "__main__":
    app()
