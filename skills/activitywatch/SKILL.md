---
name: activitywatch
description: >
  ActivityWatch computer activity statistics tool. Reads local ActivityWatch
  time-tracking data and produces daily, weekly, and monthly application usage
  reports. Also reads and writes the ActivityWatch category configuration with
  automatic backup before overwriting.
license: MIT
version: "1.0.0"
---

# ActivityWatch Computer Activity Statistics

Retrieve local ActivityWatch time-tracking data and analyze application usage, plus manage the ActivityWatch category configuration.

## Quick Reference

```bash
cd skills/activitywatch/scripts

# Activity reports (default: daily)
uv run activitywatch.py a --daily
uv run activitywatch.py activity --weekly --top 5
uv run activitywatch.py a --monthly

# Pinned to a specific day / week / month
uv run activitywatch.py a --daily 2015-02-27
uv run activitywatch.py a --weekly 2026-07-08
uv run activitywatch.py a --monthly 2025-07

# Per-day sleep/routine view (first/last activity each day, + active time)
uv run activitywatch.py a --monthly --routine
uv run activitywatch.py a --monthly 2025-07 --routine
uv run activitywatch.py a --weekly --routine

# Category configuration
uv run activitywatch.py c get
uv run activitywatch.py c get -f out.json
uv run activitywatch.py c set -f new-config.json
uv run activitywatch.py c set -f new-config.json --no-backup

# Find uncategorized apps/titles (not matched by any rule)
uv run activitywatch.py c unclassified
uv run activitywatch.py c unclassified --weekly
```

---

## CLI Commands

The script has two command groups, each with a short alias:

| Command    | Alias | Description                                                                                           |
| ---------- | ----- | ----------------------------------------------------------------------------------------------------- |
| `activity` | `a`   | Show daily, weekly, or monthly activity reports.                                                      |
| `category` | `c`   | Get, set, or inspect the ActivityWatch category configuration (including finding uncategorized apps). |

---

### `activity` — Show activity reports

```bash
uv run activitywatch.py a [--daily | --weekly | --monthly] [DATE] [--routine] [--top N] [--url URL]
```

`DATE` is an optional positional argument that pins the report to a specific
day or month instead of the current one. The format depends on the selected
period (see below). It may also be passed as `--date <value>`.

**Parameters:**

| Option              | Default                 | Description                                                                                                                                       |
| ------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATE` (positional) | current period          | Pin the report to a specific day (`YYYY-MM-DD` for `--daily`/`--weekly`, e.g. `2015-02-27`) or month (`YYYY-MM` for `--monthly`, e.g. `2025-07`). |
| `--daily`           | (default if none set)   | Show today's activity.                                                                                                                            |
| `--weekly`          | —                       | Show this week's activity (starts Monday).                                                                                                        |
| `--monthly`         | —                       | Show this month's activity.                                                                                                                       |
| `--routine`         | —                       | Per-day first/last activity times (sleep/routine view). Best with `--weekly`/`--monthly`; rejected with `--daily`.                                |
| `--top`             | `10`                    | Number of top applications to list (1–100).                                                                                                       |
| `--url`             | `http://localhost:5600` | ActivityWatch server URL.                                                                                                                         |

At most one of `--daily`/`--weekly`/`--monthly` may be set. If none is given, `--daily` is assumed.

#### Pinning to a specific day / week / month

The optional `DATE` argument lets you query any past (or current) period. The
format must match the selected period:

| Period      | `DATE` format | Example      | Resulting range                                                                       |
| ----------- | ------------- | ------------ | ------------------------------------------------------------------------------------- |
| `--daily`   | `YYYY-MM-DD`  | `2015-02-27` | That single day, from `startOfDay` to the next day's `startOfDay`.                    |
| `--weekly`  | `YYYY-MM-DD`  | `2026-07-08` | The week containing that date, respecting the server's `startOfWeek` (Monday/Sunday). |
| `--monthly` | `YYYY-MM`     | `2025-07`    | That whole month, from the 1st at `startOfDay` to the next month's `startOfDay`.      |

For the **current** day/week/month the end bound is `now` (the report is
up-to-the-minute). For **past** periods the end bound is the natural end of
that period (next day / next week / next month at `startOfDay`), so the full
period is covered. The `startOfDay` and `startOfWeek` settings are always read
from the ActivityWatch server to match the web UI.

```bash
# Activity on a specific day
uv run activitywatch.py a --daily 2015-02-27

# The week containing a specific date (week starts per server config)
uv run activitywatch.py a --weekly 2026-06-15

# A whole month
uv run activitywatch.py a --monthly 2025-07

# Equivalent flag form
uv run activitywatch.py a --monthly --date 2025-07
```

Invalid formats are rejected with a clear error, e.g. passing `2025-07-08` to
`--monthly` or `2025-07` to `--daily`.

**Output example:**

```
Daily Activity Report
Period: 2026-07-08 10:25 ~ 16:56
Active: 4h28m
Top 10 applications:
  Tabbit Browser  48m47s (18.2%)
  WorkBuddy       40m12s (15.0%)
  firefox         37m35s (14.0%)
  OpenCode        33m14s (12.4%)
  ZenlessZoneZero 26m32s (9.9%)
  ...
Total: 4h28m across 30 apps (top 10 shown, covers 98.4%)

Category breakdown:
  🎬 娱乐           1h21m (30.2%)  - ZenlessZoneZero, MuMuNxDevice, Tabbit Browser
  💼 工作           1h16m (28.6%)  - WorkBuddy, OpenCode, firefox
  📚 学习           38m26s (14.3%)  - Tabbit Browser, firefox
  🛠️ 工具          28m45s (10.7%)  - Code, firefox, MiScreenShare
  🌐 浏览           21m48s (8.1%)  - firefox
  Uncategorized  19m41s (7.3%)  - qwenpaw-desktop, Tabbit Browser, clash-verge
  💬 通讯           1m42s (0.6%)  - olk

Top apps timeline  (gap<=3m  segs>=10m  top10)
  Tabbit Browser     11:57-12:16 18m30s  15:06-15:17 10m41s
  WorkBuddy          12:26-12:41 14m9s  14:01-14:17 15m48s
  firefox            13:54-14:17 22m43s
  OpenCode           10:44-11:03 19m15s  16:22-16:34 11m47s
  ZenlessZoneZero    11:19-11:44 24m47s
  MuMuNxDevice       10:29-10:44 14m42s  11:59-12:14 14m48s
(6 of 10 apps had no segments >= 10m)
Focus sessions (>=10m): 11  |  Longest: 24m47s (ZenlessZoneZero 11:19-11:44)
```

Apps are aggregated by `data.app` (one entry per application, not per
window/tab). The display name is the `app` value as reported by
`aw-watcher-window`, with a trailing `.exe` stripped (e.g. `firefox.exe` ->
`firefox`). No window-title reverse lookup is performed — the `app` field on
Windows is inconsistent (exe name for some apps, friendly name or title for
others), so the report simply shows whichever form the watcher recorded.

Entries that resolve to the same name are merged.

- **Title line**: report title (Daily / Weekly / Monthly).
- **Period line**: `Period: <first-activity> ~ <last-activity>` - the actual first and last recorded activity timestamps in the period (local timezone), not the configured `startOfDay` bounds. This reflects when the user was really at the computer; idle/sleep/watcher-down gaps before the first and after the last event are not shown.
- **Active line**: `Active: <duration>` - the AFK-filtered active time only. No wall-clock fraction is shown, since the (often much wider) period span already implies the idle/sleep gap.
- **Top applications**: app name, duration, percentage (share of active time, sorted by duration descending). Each line is indented two spaces (no bullet/hyphen) and app names are padded to a common width so the durations and percentages align in a tidy column.
- **Total line**: total active duration and app count; when the app count exceeds `--top`, a `(top N shown, covers X.X%)` suffix is appended.
- **Category breakdown**: a top-level rollup of activity by category. Each event is classified with ActivityWatch's own semantics (every `regex` rule is tested against the app name _or_ the window title; the **deepest** matching category path wins, with ties broken by later-in-list; events matching no rule land in `Uncategorized`). Category paths roll up to their first element. `none`-type ("No rule") categories match nothing - they only act as parent folders - so they never receive events directly. The section is omitted entirely when the server has no categories configured. The same app can appear under multiple categories because classification is per-event (app + title), so e.g. a browser's time is split by what its tabs were.
- **Timeline**: per-app long activity segments (see below).
- **Focus line**: `Focus sessions (>=Nm): <count>  |  Longest: <dur> (<app> HH:MM-HH:MM)` - a focus session is any merged same-app segment at least 10 minutes (600s) long, counted across all apps; the longest single segment is also reported.
- Durations use compact formatting: `45s`, `37m`, `4h12m`, `1d3h`.

#### Timeline

Below the category breakdown, a per-app timeline lists each top app's long
activity segments. Adjacent events from the same app within 3 minutes are
merged; only segments at least 10 minutes long are shown, in chronological
order (left-to-right reads as the day's flow). Apps that have no long segments are omitted from the timeline, with a
trailing `(N of M apps had no segments >= Xm)` line summarizing what was
dropped. A line that exceeds ~120 characters is truncated with `+N more`.
Apps that switch too frequently (>= 6 long segments) collapse to one
approximate `HH:MM-HH:MM (~duration)` range with a
`[switched frequently, approximate range only]` note.

When adjacent events are merged, the segment's reported duration spans the
full start-to-end window, which includes the gap between the merged events
(not just their combined active time).

The timeline is followed by a one-line focus summary (see the Focus line
above).

#### Routine (`--routine`)

Add `--routine` to switch the report to a per-day sleep/routine view: instead
of top apps and timelines, it prints one line per day with the first and last
recorded activity time, plus the `active` duration - the AFK-filtered total
time actually spent at the computer that day. Best with `--weekly` or
`--monthly`; `--daily` is rejected (a single day has no per-day breakdown).

```bash
uv run activitywatch.py a --monthly --routine           # this month
uv run activitywatch.py a --monthly 2025-07 --routine   # a specific month
uv run activitywatch.py a --weekly --routine            # this week
```

**Output example:**

```
Monthly Routine
Period: 2026-07-01 ~ 2026-07-09
Day starts at: 04:00

  2026-07-01  08:50 ~ 03:57 (+1d)  active 9h12m
  2026-07-02  10:31 ~ 00:02 (+1d)  active 7h40m
  2026-07-03  09:00 ~ 01:07 (+1d)  active 8h05m
  2026-07-04  10:47 ~ 01:19 (+1d)  active 6h33m
  2026-07-05  11:01 ~ 02:43 (+1d)  active 10h18m
  2026-07-06  11:16 ~ 04:01 (+1d)  active 5h27m
  2026-07-07  04:01 ~ 01:28 (+1d)  active 11h02m
  2026-07-08  10:25 ~ 00:44 (+1d)  active 7h51m
  2026-07-09  10:48 ~ 14:05  (in progress)  active 3h17m
```

Each day shows the earliest and latest AFK-filtered activity time, plus the
`active` duration - the AFK-filtered total time actually spent at the computer
that day (sum of event durations), which is usually far less than the
wall-clock start~end window because idle, away, and sleep gaps are excluded. A day's
"routine day" boundary is offset by the server's `startOfDay` (e.g. `04:00`
means a 03:00 event counts toward the previous day), so late-night sessions
stay attached to the day they belong to rather than spilling into the next.
Annotations:

- `(+1d)` — the last activity ran past midnight into the next calendar day.
- `(in progress)` — today; the day is not over yet, so the end time is `now`.
- `(no activity)` — no events recorded that day (keeps the calendar contiguous).

---

### `category` — Get, set, or inspect category configuration

ActivityWatch categories are stored as a server setting (`classes`) and consist of a list of category entries, each with a name path, a classification rule, and optional metadata (color, id). Besides reading and writing the config, you can also list apps/titles that no rule matches — useful for discovering what new categories to add.

#### `category get`

```bash
uv run activitywatch.py c get [-f | --file out.json] [--url URL]
```

Read the current category configuration.

| Option         | Default                 | Description                                          |
| -------------- | ----------------------- | ---------------------------------------------------- |
| `-f`, `--file` | —                       | Write the categories to this file instead of stdout. |
| `--url`        | `http://localhost:5600` | ActivityWatch server URL.                            |

Without `-f`, prints the category list as pretty JSON to stdout. With `-f`, writes the JSON to the file and prints a confirmation.

**Output example (stdout):**

```json
[
  {
    "name": ["Work", "Programming"],
    "rule": {
      "type": "regex",
      "regex": "Code|VSCode|Cursor",
      "ignore_case": true
    },
    "id": 1,
    "data": { "color": "#A8D0F0" }
  },
  {
    "name": ["Media", "Video"],
    "rule": { "type": "regex", "regex": "YouTube|VLC", "ignore_case": true },
    "id": 2,
    "data": { "color": "#FFD0A8" }
  }
]
```

#### `category set`

```bash
uv run activitywatch.py c set -f | --file config.json [--no-backup] [--url URL]
```

Replace the category configuration from a JSON file. **The previous configuration is backed up by default** to `cache/categories-backup-<timestamp>.json` before the new one is written. Pass `--no-backup` to skip the backup.

| Option         | Default                 | Description                                            |
| -------------- | ----------------------- | ------------------------------------------------------ |
| `-f`, `--file` | (required)              | JSON file with the new category config.                |
| `--no-backup`  | Off                     | Skip backing up the current config before overwriting. |
| `--url`        | `http://localhost:5600` | ActivityWatch server URL.                              |

The input file must be a JSON array of category objects. Each object requires:

| Field  | Type        | Required | Description                                    |
| ------ | ----------- | -------- | ---------------------------------------------- |
| `name` | `list[str]` | Yes      | Category path, e.g. `["Work", "Programming"]`. |
| `rule` | `object`    | Yes      | Classification rule (see below).               |
| `id`   | `int`       | No       | Category ID (server may reassign).             |
| `data` | `object`    | No       | Metadata, e.g. `{"color": "#A8D0F0"}`.         |

Rule object:

| Field         | Type                  | Required            | Description                                   |
| ------------- | --------------------- | ------------------- | --------------------------------------------- |
| `type`        | `"regex"` or `"none"` | Yes                 | Rule type. `"none"` is a catch-all.           |
| `regex`       | `str`                 | For `type: "regex"` | Regular expression matched against app/title. |
| `ignore_case` | `bool`                | No                  | Case-insensitive matching.                    |

**Roundtrip workflow:** run `c get -f my-config.json`, edit the file, then `c set -f my-config.json` to apply changes. The backup file allows rollback if needed.

#### `category unclassified`

```bash
uv run activitywatch.py c unclassified [--daily | --weekly | --monthly] [DATE] [--url URL]
```

List app names and window titles **not matched by any `regex` category rule**. This is the counterpart to `get`/`set`: it tells you _what_ still needs a category so you can decide which rules to add.

`DATE` is an optional positional argument that pins the scan to a specific day (`YYYY-MM-DD` for `--daily`/`--weekly`) or month (`YYYY-MM` for `--monthly`), exactly like the `activity` command.

**Parameters:**

| Option              | Default                 | Description                                                                                                                                     |
| ------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATE` (positional) | current period          | Pin the scan to a specific day (`YYYY-MM-DD` for `--daily`/`--weekly`, e.g. `2015-02-27`) or month (`YYYY-MM` for `--monthly`, e.g. `2025-07`). |
| `--daily`           | (default if none set)   | Scan today's activity.                                                                                                                          |
| `--weekly`          | —                       | Scan this week's activity (starts Monday).                                                                                                      |
| `--monthly`         | —                       | Scan this month's activity.                                                                                                                     |
| `--url`             | `http://localhost:5600` | ActivityWatch server URL.                                                                                                                       |

At most one of `--daily`/`--weekly`/`--monthly` may be set. If none is given, `--daily` is assumed.

**How it works:** every `regex` rule is compiled and matched (substring search, honoring `ignore_case`) against both the app name and the window title of each event — the same logic ActivityWatch uses for classification. `none`-type (catch-all) rules are skipped, because they match everything. Any event whose app **and** title fail to match any regex rule contributes its app name and title to the output. The output lists one line per uncategorized app, with up to 3 sample window titles appended after `-` (comma-separated, `...` if truncated) — nothing else.

**Output example:**

```
Uncategorized apps and titles
Period: 2026-07-08 04:00 ~ 15:58
  ApplicationFrameHost  -  通知中心, 设置, Window Dialog, ...
  clash-verge  -  Clash Verge
  consent  -  用户账户控制(UAC)
  firefox  -  New Tab - Mozilla Firefox, GitHub: Let's build from here, ...
  qianwen  -  千问
  Super Productivity  -  Super Productivity
```

If every event is already matched by existing rules, the output ends with `All activity matched by existing category rules.`

**Typical workflow with `get` / `set`:**

1. `c unclassified` — see which apps/titles lack a category.
2. `c get -f my-config.json` — export the current config.
3. Edit the file to add new `regex` rules covering the uncategorized entries.
4. `c set -f my-config.json` — apply (previous config is backed up automatically).
5. `c unclassified` again — verify the new rules took effect.

---

## Key Rules

| Rule                         | Description                                                                                                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Server must be running       | Ensure `aw-server` is running before use (default `http://localhost:5600`).                                                                                              |
| AFK filtering                | Activity reports exclude AFK (away-from-keyboard) periods automatically.                                                                                                 |
| Timezone                     | Report headers use local timezone; queries are sent to the server in UTC.                                                                                                |
| `startOfDay` / `startOfWeek` | Day, week, and month boundaries respect the server's `startOfDay` (e.g. `04:00`) and `startOfWeek` (`Monday`/`Sunday`) settings to match the ActivityWatch web UI.       |
| Category backup              | `category set` backs up the previous config to `cache/categories-backup-<timestamp>.json` before writing. Use `--no-backup` to skip.                                     |
| Category format              | Reads/writes the `classes` server setting (the canonical format used by `aw-client`). The web UI v0.13+ `category_sets` multi-set feature is not managed by this script. |

---

## Dependencies

Managed automatically by `uv` via inline script metadata (no manual install needed):

- Python ≥ 3.12
- `aw-client` — official ActivityWatch Python client
- `cyclopts` — CLI framework
- `pydantic` — data validation

**Run with uv (recommended):**

```bash
uv run activitywatch.py a --daily
```

---

## Notes

| Note                    | Description                                                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Server dependency**   | The script requires `aw-server` to be running locally with at least one `aw-watcher-window` and `aw-watcher-afk` bucket. |
| **Hostname detection**  | Watcher bucket IDs use `socket.gethostname()` (e.g. `aw-watcher-window_THISPC`), detected automatically.                 |
| **Errors go to stderr** | Activity reports and `c get` stdout JSON go to stdout; error messages go to stderr for clean piping.                     |
| **Backup location**     | `cache/categories-backup-<YYYYMMDD-HHMMSS>.json` (atomic write: temp file + rename).                                     |
