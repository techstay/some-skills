# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "cyclopts>=4.20.0",
#     "httpx>=0.28.1",
#     "loguru>=0.7.0",
#     "python-dotenv>=1.2.2",
# ]
# ///


import os
import sys
from typing import Annotated

import httpx
from cyclopts import App, Parameter
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger.remove()
logger.add(sys.stderr, level="INFO")

app = App(
    name="notify",
    help="Send push notifications to Telegram, ntfy, Pushover, or WxPusher.",
    help_flags=["-h", "--help"],
    version_flags=["-v", "--version"],
    version="1.0.0",
)


def print_status(status: dict) -> None:
    """Print a flat status dict in YAML-like format."""
    for key, value in status.items():
        if value is None:
            continue
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, int):
            rendered = str(value)
        elif isinstance(value, str):
            rendered = value
        else:
            rendered = str(value)
        print(f"{key}: {rendered}")


def _normalize_content(content: str) -> str:
    """Normalize line endings and interpret literal ``\\n`` escape sequences.

    Shell arguments pass ``\\n`` as two literal characters (backslash + n),
    not as a real newline (0x0A). Push services render real newlines as line
    breaks but display literal ``\\n`` as plain text. This helper:
      1. Normalizes Windows/old-Mac line endings (``\\r\\n``, ``\\r``) to LF.
      2. Converts literal ``\\n`` escape sequences to real newlines.
    """
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    content = content.replace("\\n", "\n")
    return content


@app.command(name="telegram", help="Send a notification via Telegram Bot API.")
def telegram(
    title: Annotated[str, Parameter(help="Notification title. Pass empty string for no title.")],
    content: Annotated[str, Parameter(help="Notification message content.")],
) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env or environment.")
        return False

    content = _normalize_content(content)
    text = f"<b>{title}</b>\n\n{content}" if title else content
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        resp = httpx.post(url, json=payload, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("ok"):
            message_id = data.get("result", {}).get("message_id")
            print_status({
                "status": "success",
                "service": "telegram",
                "message_id": message_id,
            })
            return True
        error = data.get("description", "Unknown Telegram API error")
        logger.error("Telegram API error: {}", error)
        print_status({
            "status": "failed",
            "service": "telegram",
            "error": error,
        })
        return False
    except httpx.HTTPError as e:
        logger.error("Telegram request failed: {}", e)
        print_status({
            "status": "failed",
            "service": "telegram",
            "error": str(e),
        })
        return False


@app.command(name="ntfy", help="Send a notification via ntfy.")
def ntfy(
    title: Annotated[str, Parameter(help="Notification title. Pass empty string for no title.")],
    content: Annotated[str, Parameter(help="Notification message content.")],
) -> bool:
    topic = os.getenv("NTFY_TOPIC")
    server = os.getenv("NTFY_SERVER", "https://ntfy.sh")
    token = os.getenv("NTFY_TOKEN")
    if not topic:
        logger.error("NTFY_TOPIC must be set in .env or environment.")
        return False

    url = str(server).rstrip("/")
    content = _normalize_content(content)
    payload: dict[str, object] = {"topic": topic, "message": content}
    if title:
        payload["title"] = title
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=15.0)
        if 200 <= resp.status_code < 300:
            print_status({
                "status": "success",
                "service": "ntfy",
                "topic": topic,
            })
            return True
        logger.error("ntfy returned HTTP {}", resp.status_code)
        print_status({
            "status": "failed",
            "service": "ntfy",
            "http_status": resp.status_code,
            "error": resp.text,
        })
        return False
    except httpx.HTTPError as e:
        logger.error("ntfy request failed: {}", e)
        print_status({
            "status": "failed",
            "service": "ntfy",
            "error": str(e),
        })
        return False


@app.command(name="wxpusher", help="Send a notification via WxPusher.")
def wxpusher(
    title: Annotated[str, Parameter(help="Notification title. Pass empty string for no title.")],
    content: Annotated[str, Parameter(help="Notification message content.")],
) -> bool:
    app_token = os.getenv("WXPUSHER_APP_TOKEN")
    uid_raw = os.getenv("WXPUSHER_UID")
    if not app_token or not uid_raw:
        logger.error("WXPUSHER_APP_TOKEN and WXPUSHER_UID must be set in .env or environment.")
        return False

    uids = [uid.strip() for uid in uid_raw.split(",") if uid.strip()]
    if not uids:
        logger.error("WXPUSHER_UID contains no valid UIDs.")
        return False

    content = _normalize_content(content)
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload: dict[str, object] = {
        "appToken": app_token,
        "content": content,
        "contentType": 1,
        "uids": uids,
    }
    if title:
        payload["summary"] = title

    try:
        resp = httpx.post(url, json=payload, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 1000:
            print_status({
                "status": "success",
                "service": "wxpusher",
            })
            return True
        error = data.get("msg", "Unknown WxPusher API error")
        logger.error("WxPusher API error: {}", error)
        print_status({
            "status": "failed",
            "service": "wxpusher",
            "error": error,
        })
        return False
    except httpx.HTTPError as e:
        logger.error("WxPusher request failed: {}", e)
        print_status({
            "status": "failed",
            "service": "wxpusher",
            "error": str(e),
        })
        return False


if __name__ == "__main__":
    app()
