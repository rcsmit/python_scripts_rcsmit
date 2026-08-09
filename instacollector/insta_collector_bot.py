"""
Instagram Collector Telegram Bot
=================================

Receives Instagram post/reel links sent (or forwarded) to a Telegram bot and
appends them as rows to a Google Sheet, so a JS page can later read that
sheet and render a filtered "collection" for whoever the link is shared with.

# version : 20260809-140000 - Initial version: link capture, collection switching, Google Sheets append
# version : 20260809-141500 - Auto-load configuration from .env via python-dotenv
current_version = "20260809-141500"
"""

from __future__ import annotations

import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --------------------------------------------------------------------------- #
# Configuration (all via environment variables, loaded from .env if present)
# --------------------------------------------------------------------------- #

load_dotenv()  # picks up a .env file next to this script, created by setup_env.py

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
WORKSHEET_NAME = os.environ.get("WORKSHEET_NAME", "Blad1")
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get(
    "GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"
)
DEFAULT_COLLECTION = os.environ.get("DEFAULT_COLLECTION", "default")

# Optional allowlist: comma-separated Telegram numeric user IDs.
# Leave ALLOWED_USER_IDS unset to allow anyone who has the bot link.
_raw_allowed = os.environ.get("ALLOWED_USER_IDS", "").strip()
ALLOWED_USER_IDS: set[int] = (
    {int(uid.strip()) for uid in _raw_allowed.split(",") if uid.strip()}
    if _raw_allowed
    else set()
)

STATE_FILE = Path(os.environ.get("STATE_FILE", "chat_state.json"))

SHEET_COLUMNS = [
    "id",
    "collection",
    "url",
    "date_added",
    "added_by",
    "caption",
    "tags",
    "type",
    "status",
]

INSTAGRAM_URL_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?P<kind>reel|reels|p|tv)/(?P<code>[A-Za-z0-9_\-]+)/?[^\s]*",
    re.IGNORECASE,
)
HASHTAG_RE = re.compile(r"#(\w+)")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("insta_collector_bot")


# --------------------------------------------------------------------------- #
# Per-chat state (which collection new links currently go into)
# --------------------------------------------------------------------------- #


@dataclass
class ChatState:
    active_collection: str = DEFAULT_COLLECTION


class ChatStateStore:
    """Tiny JSON-backed store so the active collection survives bot restarts."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, ChatState] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        import json

        try:
            raw = json.loads(self._path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Could not read state file, starting fresh: %s", e)
            return
        for chat_id, entry in raw.items():
            self._data[chat_id] = ChatState(active_collection=entry.get("active_collection", DEFAULT_COLLECTION))

    def _save(self) -> None:
        import json

        serializable = {
            chat_id: {"active_collection": state.active_collection}
            for chat_id, state in self._data.items()
        }
        try:
            self._path.write_text(json.dumps(serializable, indent=2))
        except OSError as e:
            logger.error("Could not write state file: %s", e)

    def get(self, chat_id: int) -> ChatState:
        return self._data.setdefault(str(chat_id), ChatState())

    def set_collection(self, chat_id: int, collection: str) -> None:
        self.get(chat_id).active_collection = collection
        self._save()


state_store = ChatStateStore(STATE_FILE)


# --------------------------------------------------------------------------- #
# Google Sheets
# --------------------------------------------------------------------------- #


class SheetWriter:
    """Thin wrapper around gspread, tolerant of a header row already present."""

    def __init__(self, spreadsheet_id: str, worksheet_name: str, creds_file: str) -> None:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
        client = gspread.authorize(creds)
        self._sheet = client.open_by_key(spreadsheet_id)
        self._worksheet_name = worksheet_name
        self._ws = self._get_or_create_worksheet()

    def _get_or_create_worksheet(self) -> gspread.Worksheet:
        try:
            ws = self._sheet.worksheet(self._worksheet_name)
        except gspread.WorksheetNotFound:
            ws = self._sheet.add_worksheet(
                title=self._worksheet_name, rows=1000, cols=len(SHEET_COLUMNS)
            )
        header = ws.row_values(1)
        if header != SHEET_COLUMNS:
            ws.update("A1", [SHEET_COLUMNS])
        return ws

    def append_row(self, row: dict[str, str]) -> None:
        values = [row.get(col, "") for col in SHEET_COLUMNS]
        self._ws.append_row(values, value_input_option="USER_ENTERED")

    def recent_rows(self, collection: str, limit: int = 5) -> list[dict[str, str]]:
        records = self._ws.get_all_records()
        matching = [r for r in records if str(r.get("collection", "")) == collection]
        return matching[-limit:]


sheet_writer: Optional[SheetWriter] = None


def get_sheet_writer() -> SheetWriter:
    global sheet_writer
    if sheet_writer is None:
        sheet_writer = SheetWriter(SPREADSHEET_ID, WORKSHEET_NAME, GOOGLE_SERVICE_ACCOUNT_FILE)
    return sheet_writer


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #


def instagram_type_from_kind(kind: str) -> str:
    kind = kind.lower()
    if kind in ("reel", "reels"):
        return "reel"
    if kind == "tv":
        return "igtv"
    return "post"


def extract_links(text: str) -> list[tuple[str, str]]:
    """Return list of (clean_url, type) for every Instagram link found in text."""
    results = []
    for match in INSTAGRAM_URL_RE.finditer(text):
        clean_url = f"https://www.instagram.com/{match.group('kind').lower()}/{match.group('code')}/"
        results.append((clean_url, instagram_type_from_kind(match.group("kind"))))
    return results


def extract_tags(text: str) -> str:
    return ",".join(HASHTAG_RE.findall(text))


def extract_caption(text: str, urls_found: list[str]) -> str:
    caption = text
    for url in urls_found:
        caption = caption.replace(url, "")
    caption = HASHTAG_RE.sub("", caption)
    return caption.strip()


def is_allowed(user_id: int) -> bool:
    return not ALLOWED_USER_IDS or user_id in ALLOWED_USER_IDS


# --------------------------------------------------------------------------- #
# Command handlers
# --------------------------------------------------------------------------- #


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Send or forward me an Instagram post/reel link and I'll add it to your collection.\n\n"
        "Commands:\n"
        "/collection <name> — switch which collection new links go into\n"
        "/whoami — show the active collection for this chat\n"
        "/list — show the last 5 links added to the active collection\n\n"
        f"Current collection: {state_store.get(update.effective_chat.id).active_collection}"
    )


async def cmd_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: /collection <name>\n"
            f"Active collection is currently: {state_store.get(update.effective_chat.id).active_collection}"
        )
        return
    name = " ".join(context.args).strip()
    state_store.set_collection(update.effective_chat.id, name)
    await update.message.reply_text(f"Active collection set to: {name}")


async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    collection = state_store.get(update.effective_chat.id).active_collection
    await update.message.reply_text(f"Active collection: {collection}")


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    collection = state_store.get(update.effective_chat.id).active_collection
    try:
        rows = get_sheet_writer().recent_rows(collection)
    except Exception as e:
        logger.exception("Failed to read sheet")
        await update.message.reply_text(f"Could not read the sheet: {e}")
        return
    if not rows:
        await update.message.reply_text(f"No links yet in '{collection}'.")
        return
    lines = [f"Last {len(rows)} in '{collection}':"]
    for r in rows:
        lines.append(f"- {r.get('url')}")
    await update.message.reply_text("\n".join(lines))


# --------------------------------------------------------------------------- #
# Message handler — the actual link capture
# --------------------------------------------------------------------------- #


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user

    if user is None or not is_allowed(user.id):
        await message.reply_text("Sorry, you're not authorized to add links to this collection.")
        logger.info("Rejected message from unauthorized user_id=%s", user.id if user else None)
        return

    text = message.text or message.caption or ""
    if not text:
        return

    found = extract_links(text)
    if not found:
        await message.reply_text(
            "I didn't find an Instagram post/reel link in that message. "
            "Send a link like https://www.instagram.com/reel/XXXXXXX/"
        )
        return

    collection = state_store.get(update.effective_chat.id).active_collection
    tags = extract_tags(text)
    caption = extract_caption(text, [url for url, _ in found])
    added_by = user.username or user.first_name or str(user.id)
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    try:
        writer = get_sheet_writer()
    except Exception as e:
        logger.exception("Failed to connect to Google Sheets")
        await message.reply_text(f"Could not connect to the sheet: {e}")
        return

    added = []
    for url, insta_type in found:
        row = {
            "id": uuid.uuid4().hex[:12],
            "collection": collection,
            "url": url,
            "date_added": now_iso,
            "added_by": added_by,
            "caption": caption,
            "tags": tags,
            "type": insta_type,
            "status": "active",
        }
        try:
            writer.append_row(row)
            added.append(url)
        except Exception as e:
            logger.exception("Failed to append row for %s", url)
            await message.reply_text(f"Failed to save {url}: {e}")

    if added:
        plural = "s" if len(added) > 1 else ""
        await message.reply_text(
            f"Added {len(added)} link{plural} to '{collection}'."
        )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("collection", cmd_collection))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, handle_message))

    logger.info("Bot starting (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
