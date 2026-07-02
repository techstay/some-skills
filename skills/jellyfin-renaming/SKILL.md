---
name: jellyfin-renaming
description: >
  Manually rename Jellyfin movie, TV show, anime, special episode, external subtitle,
  external audio, movie directory, and TV show directory names for reliable library
  matching. Use when the user wants to automatically rename real media files or
  folders on disk, clean messy release filenames, convert files to Jellyfin movie or
  SxxExx show naming, align subtitles with videos, preserve traceability, or verify
  Jellyfin-compatible media naming without using bulk renaming scripts or paid
  renaming tools.
license: MIT
---

# Jellyfin Renaming

Manually decide and apply Jellyfin-compatible movie and TV show file and directory renames. Treat every rename as a reviewed mapping, not a blind bulk text transformation.

## Core Rule

When the user gives real filesystem paths and asks to rename media, perform the rename on disk after building and checking a mapping. If the user gives only a list of names or explicitly asks for suggestions, return exactly one output filename for each input filename, in the same order.

If a movie, episode, special, subtitle, audio track, version label, or language suffix cannot be identified with confidence, keep the original name.

## Absolute Prohibition: Never Delete Files

**Never delete any file under any circumstance.** Every operation that would remove a file must instead move that file to a `Rubbish/` folder inside the affected movie or show folder. This rule has no exceptions — not for duplicates, not for noise files, not for files the user calls "junk". After all operations are complete, always remind the user:

> ⚠️ Please review the `Rubbish/` folder and delete it manually when you are sure the files inside are no longer needed.

## Manual Workflow

| Step | What to do |
| ---- | ---------- |
| 1. Identify context | Use the movie or series title, year, season, folder name, and surrounding files before deciding a final name. |
| 2. Remove noise | Drop release group, source, codec, resolution, audio channel, CRC/hash, website, and bracketed download tags unless they are needed as movie version labels. |
| 3. Preserve evidence | Keep extensions, subtitle language/flag suffixes, multi-episode ranges, split-part markers, edition/version labels, and meaningful special labels. |
| 4. Match Jellyfin | Prefer official Jellyfin movie and show patterns, including movie folders, season folders, SxxExx markers, version labels, and external-track suffixes. |
| 5. Refuse guesses | If the input does not contain enough information, output the original filename unchanged. |
| 6. Check safety | Before renaming, check for path collisions, invalid characters, case-only conflicts, and ambiguous matches. |
| 7. Apply carefully | Rename files before parent directories when needed; rename deeper paths before shallower paths. |
| 8. Record traceability | After completing all renames for a movie or show, create a rename log that records every original path and final path. |

## Automatic Rename Execution

Use this workflow when the user asks to rename actual directories or files.

| Step | Requirement |
| ---- | ----------- |
| **Plan first** | Before executing any filesystem operation, output a numbered step-by-step plan listing every rename, every move-to-Rubbish, and every new directory to be created. Wait for implicit or explicit user acknowledgement, then execute the steps one by one in the listed order. |
| Inventory | List only the target movie/show folder and the files needed for the task. Do not modify unrelated media. |
| Mapping | Build a reviewed old-path to new-path mapping for files and directories. |
| Conflict check | Stop before renaming if two sources map to the same target, a target already exists, or a rename would move media outside the intended folder. |
| Directory order | Rename files first, then season folders, then show/movie folders. For nested directory renames, process deepest paths first. |
| Case-only renames | On case-insensitive filesystems, use a temporary intermediate name before applying a case-only rename. |
| Subtitle pairing | Rename subtitles and external audio after the corresponding video basename is finalized. |
| Unwanted files | Never delete files directly. Move any file that should be removed to `Rubbish/` inside the affected movie or show folder. After all operations are complete, remind the user to review `Rubbish/` and delete it manually. |
| Log | Create or append `rename-log.md` in the affected movie or show folder after the rename succeeds. |

Do not use generic bulk renaming scripts or paid renaming tools. It is acceptable to use normal filesystem operations to apply the reviewed mapping.

## TMDB Lookup Script

Use the local TMDB helper when a movie or series title, year, media type, or provider id needs confirmation before renaming.

Requirements:

| Item | Details |
| ---- | ------- |
| Environment variable | `TMDB_API_KEY` must contain a TMDB API read access token. |
| Working directory | Run commands from `skills/jellyfin-renaming/scripts/`. |
| Output | The script prints JSON records with `id`, `title`, `original_title`, `overview`, `release_date`, `media_type`, `vote_average`, and `poster_path`. |

Commands:

```powershell
uv run tmdb.py "Movie or Show Title"
uv run tmdb.py "Movie or Show Title" --lang en-US --limit 5 --pretty
uv run tmdb.py --help
```

Use TMDB results as supporting evidence, not as an automatic rename source. Pick the result that matches the surrounding files, release year, original title, and media type.

## Jellyfin Movie Rules

Use these rules for Movies libraries.

| Item | Preferred format | Notes |
| ---- | ---------------- | ----- |
| Movie folder | `Movie Name (year) [providerid-id]` | Each movie should have its own folder. `year` and provider id are optional, but improve matching. Examples: `[tmdbid-12345]`, `[imdbid-tt0000000]`. |
| Main movie file | `Movie Name (year) [providerid-id].ext` | The video filename should match the folder name exactly, before the extension. |
| Movie with no year | `Movie Name/Movie Name.ext` | Acceptable, but less reliable for matching. |
| External subtitle or audio | `Movie Name (year).language-or-flags.ext` | The basename should match the movie video basename. Use dot-separated language, title, and flag suffixes. |
| Disc folders | `VIDEO_TS` or `BDMV` inside the movie folder | Supported for movies and music videos, but not for multiple versions, multiple parts, or external subtitle/audio tracks. |
| Disc images | `.iso` and similar | May work but are not supported. Prefer remuxing to `mkv` or extracting to `VIDEO_TS` or `BDMV`. |

### Movie Versions

Jellyfin supports multiple versions of the same movie in one movie folder only when every version filename begins with the parent folder name exactly.

```text
Movie (2021) [imdbid-tt12801262]/
Movie (2021) [imdbid-tt12801262] - 2160p.mp4
Movie (2021) [imdbid-tt12801262] - 1080p.mp4
Movie (2021) [imdbid-tt12801262] - Directors Cut.mp4
```

Rules:

| Requirement | Details |
| ----------- | ------- |
| Exact prefix | The filename must start with the folder name character-for-character, including year and provider id. |
| Version separator | Use space, hyphen, space: ` - `. The hyphen is required. |
| Version label | Labels are user-defined, such as `2160p`, `1080p`, `Directors Cut`, or `[Extended Cut]`. |
| Avoid unsupported separators | Do not use periods or commas as the version separator. |
| Missing label | Without a version label, Jellyfin may treat files as separate movies. |

### 3D Movies

Preserve 3D tags when present. The first 3D tag must be `3D`, combined with one supported format tag.

| 3D format | Flag |
| --------- | ---- |
| half side by side | `hsbs` |
| full side by side | `fsbs` |
| half top and bottom | `htab` |
| full top and bottom | `ftab` |
| Multiview Video Coding | `mvc` |

Valid examples:

```text
Awesome 3D Movie (2022).3D.FTAB.mp4
Awesome 3D Movie (2022)_3D_htab.mp4
Awesome 3D Movie (2022)-3d-hsbs.mp4
Awesome 3D Movie (2022) - 3D_FTAB.mp4
```

### Multi-Part Movies

For one movie split across multiple files, preserve supported part markers.

```text
Movie Name (2010)/
Movie Name-cd1.mkv
Movie Name-cd2.mkv
Movie Name-cd3.mkv
```

Supported part types: `cd`, `dvd`, `part`, `pt`, `disc`, `disk`.

Supported separators between part type and part number: space, `.`, `-`, `_`, or no separator. Part numbers can be numbers or letters `a` through `d`.

Do not combine multi-part naming with multiple-version naming.

## Jellyfin TV Show Rules

Use these rules for Shows libraries.

| Item | Preferred format | Notes |
| ---- | ---------------- | ----- |
| Series folder | `Series Name (year) [providerid-id]` | `year` and provider id are optional, but improve matching. |
| Season folder | `Season 01` | Officially `Season *`; do not abbreviate to `S01` or `SE01`. Padding with zeroes is recommended. |
| Regular episode | `Series Name S01E01.ext` | Title may be appended if useful: `Series Name S01E01 Episode Title.ext`. |
| Multi-episode file | `Series Name S01E01-E02.ext` | Jellyfin displays it as one entry with metadata from multiple episodes. Prefer split files when possible. |
| Split same episode | `Series Name S02E03 Part 1.ext`, `Series Name S02E03 Part 2.ext` | Use only when one episode is split across multiple files. |
| Specials with provider metadata | `Season 00/Series Name S00E01.ext` | Special numbering varies by metadata provider. Verify before assigning numbers. |
| Specials without provider metadata | `Season 00/Descriptive Special Name.ext` | Prefer a descriptive name over guessed `S00E##` to avoid wrong metadata. |

## Episode Renaming

When the user provides a series name and season, normalize regular episodes to:

```text
Series Name S01E01.ext
```

Rules:

| Situation | Output |
| --------- | ------ |
| Single regular episode | `Series Name S01E01.ext` |
| Consecutive combined episodes | `Series Name S01E07-E08.ext` |
| Existing correct `SxxExx` | Keep the episode marker; only remove obvious noise if the user asked for cleanup. |
| Absolute anime numbering only | Convert only if the season/episode mapping is clear from context or metadata; otherwise keep original. |
| No reliable episode marker | Keep original filename. |

Do not invent episode titles. Include titles only when they are already clear and useful.

## Anime Specials, OP, ED, OVA, OAD

Anime downloads often label extras as `OP`, `NCOP`, `ED`, `NCED`, `SP`, `OVA`, or `OAD`. Handle them carefully:

| Case | Jellyfin-safe choice |
| ---- | -------------------- |
| Metadata provider has a matching special number | Put under `Season 00` and use `Series Name S00E##.ext`. |
| No known provider special number | Use a descriptive filename in `Season 00`, such as `NCOP 01.ext` or `OVA 01.ext`. |
| User specifically wants suffix-style extras | Use Jellyfin extra suffixes such as `-extra`, `-clip`, `-featurette`, or `.trailer` only when appropriate. |

Keep the original special type label when it matters. Do not force every OP/ED/OVA into a guessed `S00E##`.

## Subtitle and Audio Matching

External subtitles and audio tracks should share the exact video basename, then add dot-separated language, title, or flag parts before the final extension.

```text
Film (1986).mkv
Film (1986).default.en.forced.ass
Series Name S01E01.mkv
Series Name S01E01.ja.ass
Series Name S01E01.commentary.ja.aac
```

Supported flags include `default`, `forced`, `foreign`, `sdh`, `cc`, and `hi`. Multiple suffix parts are dot-separated.

When matching subtitle files to renamed videos:

| Rule | Behavior |
| ---- | -------- |
| Subtitle clearly matches one video | Rename subtitle basename to the video basename and keep language/flag suffixes. |
| Subtitle has `.ass`, `.ssa`, `.srt`, `.vtt`, or similar extension | Preserve the subtitle extension exactly. |
| Subtitle has language suffixes such as `.sc`, `.tc`, `.chs`, `.cht`, `.ja`, `.en`, or `.en_us` | Preserve those suffixes unless the user asks to normalize language codes. |
| Multiple possible video matches | Keep the subtitle filename unchanged. |
| Subtitle list order matters | Return subtitle outputs in the exact order provided by the user. |

## Extras Reference

Jellyfin recognizes movie, show, season, and music-video extras by folder, exact filename, or suffix.

| Method | Supported values |
| ------ | ---------------- |
| Extra folders | `behind the scenes`, `deleted scenes`, `interviews`, `scenes`, `samples`, `shorts`, `featurettes`, `clips`, `other`, `extras`, `trailers`, `theme-music`, `backdrops` |
| Exact filenames | `trailer.ext`, `sample.ext` |
| Extra suffixes | `-trailer`, `.trailer`, `_trailer`, ` trailer`, `-sample`, `.sample`, `_sample`, ` sample`, `-scene`, `-clip`, `-interview`, `-behindthescenes`, `-deleted`, `-deletedscene`, `-featurette`, `-short`, `-other`, `-extra` |

Use extras only when the file is truly supplemental. Do not turn normal show specials or OVAs into extras if they are listed as episodes by the metadata provider.

## Movie Images

Jellyfin supports local artwork files placed directly inside the movie folder. Local files take priority over artwork fetched from online metadata providers.

### Generic Image Filenames

Use these filenames inside the movie folder for Jellyfin to recognize them automatically:

| Image type | Accepted filenames | Notes |
| ---------- | ------------------ | ----- |
| Primary (poster) | `poster.jpg`, `folder.jpg`, `cover.jpg` | Main movie cover shown in library grids. |
| Backdrop (fanart) | `backdrop.jpg`, `backdrop.webp` | Background shown on the movie detail page. |
| Logo | `logo.png`, `logo.svg` | Transparent title logo overlaid on artwork. |
| Banner | `banner.jpg` | Wide strip image used in banner view. |
| Thumb | `thumb.jpg` | Landscape thumbnail used in some views. |
| Art (clearart) | `art.png` | Character art or promotional transparent PNG. |
| Disc | `disc.png`, `disc.jpg` | Disc cover used in some themes. |

Multiple backdrops are supported by appending a number:

```text
Movie Name (2020)/
  Movie Name (2020).mkv
  poster.jpg
  backdrop.jpg
  backdrop-1.jpg
  backdrop-2.jpg
  logo.png
```

### Media-Prefixed Image Filenames

Alternatively, name the image with the same basename as the video file and append a hyphen-separated image type:

| Image type | Filename pattern | Example |
| ---------- | ---------------- | ------- |
| Primary (poster) | `<video-basename>-poster.ext` | `Movie Name (2020)-poster.jpg` |
| Backdrop | `<video-basename>-backdrop.ext` | `Movie Name (2020)-backdrop.jpg` |
| Logo | `<video-basename>-logo.ext` | `Movie Name (2020)-logo.png` |
| Banner | `<video-basename>-banner.ext` | `Movie Name (2020)-banner.jpg` |
| Thumb | `<video-basename>-thumb.ext` | `Movie Name (2020)-thumb.jpg` |

Using generic filenames (`poster.jpg`, `backdrop.jpg`) is preferred for simplicity. Use media-prefixed filenames when multiple image sets must coexist in the same folder.

### Supported Image Formats

`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`, `.tbn`

Prefer `.jpg` for photos and `.png` for transparent images such as logos and clearart.

### Image Handling Rules

| Rule | Behavior |
| ---- | -------- |
| Local files present | Jellyfin uses local files and skips fetching that image type from online providers. |
| Multiple backdrops | `backdrop.jpg` is the primary; `backdrop-1.jpg`, `backdrop-2.jpg`, … are additional. |
| No local image | Jellyfin fetches and caches the image from the configured metadata provider. |
| Embedded images | Jellyfin can extract artwork embedded in video containers if the Embedded Image Extractor plugin is enabled in library settings. |
| Metadata refresh | After adding image files to an existing folder, run a library scan or trigger Refresh Metadata to apply them. |

### Image Renaming Guidelines

When renaming a movie folder or its video files, rename or verify image files in the same pass:

- Generic image filenames (`poster.jpg`, `backdrop.jpg`) do not need renaming when the movie folder is renamed; they stay in place.
- Media-prefixed image filenames must be updated to match the new video basename.
- Do not remove or discard existing local artwork files unless the user explicitly requests it.
- Record image file renames in the rename log alongside video and subtitle renames.

## Rename Log

After all files and directories for a movie or show have been renamed, create a log file in that movie or show folder so the original paths can be traced later.

Recommended log filename:

```text
rename-log.md
```

Recommended content:

```markdown
# Rename Log

- Media: Movie or Series Name (year)
- Date: YYYY-MM-DD
- Scope: movie, season, show, subtitles, or mixed

| Original filename | New filename | Notes |
| ----------------- | ------------ | ----- |
| Original.Name.1080p.x265.mkv | Movie Name (2020).mkv | Removed release noise. |
```

Rules:

| Requirement | Details |
| ----------- | ------- |
| Record every rename | Include renamed directories, video files, subtitle files, audio tracks, NFO files, and relevant extra files. |
| Use paths when executing | When actual filesystem renames were performed, record relative paths from the affected movie or show folder, not just basenames. |
| Preserve unchanged files when useful | If a file or directory was reviewed but left unchanged because it was uncertain or already correct, record that in `Notes`. |
| Keep the log local | Store the log in the affected movie or series folder, not in a global location. |
| Do not overwrite history | Append a new dated section if `rename-log.md` already exists. |

## Execution and Output Contract

When asked to rename real files or directories:

| Requirement | Details |
| ----------- | ------- |
| Apply renames | Perform the filesystem renames after the mapping and safety checks pass. |
| Stop on ambiguity | If any planned rename is ambiguous or unsafe, do not partially apply that group; report what needs clarification. |
| Report concise results | Summarize what was renamed and where the log was written. |
| Preserve extensions | Keep `.mkv`, `.mp4`, `.ass`, `.ssa`, `.srt`, `.vtt`, `.aac`, etc. |
| Preserve uncertainty | Keep original filenames when unsure. |
| Avoid filesystem-invalid characters | Do not introduce `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, or `*`. |
| Never delete directly | Move any file that would be deleted to a `Rubbish/` folder inside the affected movie or show folder instead of removing it. After all operations complete, remind the user: "Please review `Rubbish/` and delete it manually when you are sure the files are no longer needed." |

When asked only to generate proposed filenames:

| Requirement | Details |
| ----------- | ------- |
| No explanation | Output filenames only unless the user asks for reasoning or a rename log. |
| One line per input | Preserve count and order exactly. |
| Preserve extensions | Keep `.mkv`, `.mp4`, `.ass`, `.ssa`, `.srt`, `.vtt`, `.aac`, etc. |
| Preserve uncertainty | Keep original filenames when unsure. |
| Avoid filesystem-invalid characters | Do not introduce `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, or `*`. |

## Common Corrections

| Problem | Prefer |
| ------- | ------ |
| `Movie.Name.2020.1080p.x265.mkv` | `Movie Name (2020).mkv` |
| `Movie Name (2020) 4K.mkv` | `Movie Name (2020) - 4K.mkv` when it is a version label. |
| `Movie Name (2020).Directors.Cut.mkv` | `Movie Name (2020) - Directors Cut.mkv` |
| Movie version filename does not start with folder name | Start with the exact folder name, then add ` - Version Label`. |
| `Season S01/` or `S01/` | `Season 01/` |
| `Show S1E1.mkv` | `Show S01E01.mkv` |
| `Show 01.mkv` with known season | `Show S01E01.mkv` |
| `Show S01 E01.mkv` | `Show S01E01.mkv` |
| `Show S01E01 [1080p][x265][AAC].mkv` | `Show S01E01.mkv` |
| `subtitle.ass` for a known video | `Show S01E01.ass` or `Movie Name (2020).ass` |
| Guessed special number | Keep descriptive name or original filename until verified. |

## Quality Checklist

- Confirm output line count equals input line count.
- Confirm every extension is preserved.
- Confirm movie files match their movie folder basename unless they are versions, 3D variants, or multi-part files.
- Confirm movie version files start with the exact folder name and use ` - ` before the label.
- Confirm subtitle language, title, and flag suffixes are preserved.
- Confirm multi-episode and multi-part ranges remain represented.
- Confirm no guessed episode, special, movie year, or provider id was introduced.
- Confirm season folders are `Season *`, preferably padded such as `Season 01`.
- Confirm `rename-log.md` is created or appended after the full movie or show rename is complete.
