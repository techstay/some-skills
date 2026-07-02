---
name: push-and-notify
description: >
  Push message notifications to multiple endpoints. Supports Telegram, ntfy,
  and WxPusher. Use when the user asks to send a notification, push a message,
  alert via Telegram/ntfy/WxPusher, or notify endpoints.
  Each subcommand takes a title and content; services without native title
  support merge them internally.
license: MIT
version: "1.0.0"
---

# Push and Notify

Sends push notifications to Telegram, ntfy, or WxPusher from a single CLI script. Each service is an independent subcommand — set credentials only for the ones you use.

## Quick Reference

```bash
cd skills/push-and-notify/scripts

# Telegram
uv run notify.py telegram "Server Alert" "CPU usage exceeded 90%"

# ntfy
uv run notify.py ntfy "Build Done" "Deployment completed successfully"

# WxPusher
uv run notify.py wxpusher "Hello" "world"

# No title (pass empty string)
uv run notify.py telegram "" "Quick message without a title"
```

---

## Subcommands

| Subcommand | Service  | Native title | Example                                       |
| ---------- | -------- | ------------ | --------------------------------------------- |
| `telegram` | Telegram | No           | `uv run notify.py telegram "Title" "Content"` |
| `ntfy`     | ntfy     | Yes          | `uv run notify.py ntfy "Title" "Content"`     |
| `wxpusher` | WxPusher | Yes          | `uv run notify.py wxpusher "Title" "Content"` |

Services without native title support (Telegram) merge the title into the message body.

---

## Setup

1. Copy `scripts/.env.example` to `scripts/.env`.
2. Fill in the variables for the service(s) you want to use.
3. `.env` is gitignored and never committed.

Each subcommand is independent — set only the environment variables for the service you intend to use.

### Telegram

| Variable             | Required | Description               |
| -------------------- | -------- | ------------------------- |
| `TELEGRAM_BOT_TOKEN` | Yes      | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID`   | Yes      | Target chat ID or user ID |

### ntfy

| Variable      | Required | Description                                  |
| ------------- | -------- | -------------------------------------------- |
| `NTFY_TOPIC`  | Yes      | ntfy topic name                              |
| `NTFY_SERVER` | No       | ntfy server URL (default: `https://ntfy.sh`) |
| `NTFY_TOKEN`  | No       | Bearer token if the topic requires auth      |

### WxPusher

| Variable             | Required | Description                                     |
| -------------------- | -------- | ----------------------------------------------- |
| `WXPUSHER_APP_TOKEN` | Yes      | WxPusher application token                      |
| `WXPUSHER_UID`       | Yes      | UID(s), comma-separated for multiple recipients |

---

## Output Format

Each subcommand prints YAML-like status text to stdout; `loguru` writes errors to stderr. Determine success by reading the `status` field (`success` or `failed`).

Success (Telegram also returns `message_id`):

```yaml
status: success
service: telegram
message_id: 42
```

Failure (always includes an `error` field):

```yaml
status: failed
service: ntfy
error: NTFY_TOPIC must be set in .env or environment.
```

ntfy HTTP failures additionally include `http_status`.

---

## Key Rules

| Rule                                    | Description                                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Title and content are always positional | Invoke as `uv run notify.py <service> <title> <content>`.                                        |
| Use empty string for no title           | Pass `""` as the title when a service should not display a title.                                |
| Each subcommand is independent          | Set only the environment variables for the service you intend to use.                            |
| Read `status` from stdout               | Output is `status: success` or `status: failed`; failures include an `error` field (see above).  |
| Multi-line content is normalized        | Line endings and literal `\n` escapes are converted to real newlines before sending (see below). |

---

## Multi-line Content

All subcommands normalize content before sending, so newlines render correctly on every service:

1. Windows/old-Mac line endings (`\r\n`, `\r`) are converted to LF (`\n`).
2. Literal `\n` escape sequences (two characters: backslash + `n`, as typically passed by shell arguments) are converted to real newline characters (0x0A).

This means multi-line content works regardless of how you pass it:

```bash
# Literal \n in shell quotes (converted to real newlines)
uv run notify.py wxpusher "Report" "Line 1\nLine 2\nLine 3"

# Real newlines via command substitution
uv run notify.py telegram "Log" "$(cat logfile.txt)"

# Heredoc-style real newlines
uv run notify.py ntfy "Build" "Step 1
Step 2
Step 3"
```

All three services render real newline characters as line breaks. WxPusher uses `contentType=1` (text), which correctly displays newlines in WeChat — no need to switch to HTML or markdown just for line breaks.
