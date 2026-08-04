"""
Batch receipt OCR processor using Claude Vision API.
Processes all images in a TODO folder, stores results in SQLite,
and moves processed images to a DONE folder.

Usage:
    python receipt_batch.py
    python receipt_batch.py --todo C:\\receipts\\todo --done C:\\receipts\\done --db C:\\receipts\\receipts.db

Dependencies:
    pip install anthropic tqdm
"""

# version : 20260526-113507 - Initial version: batch OCR, SQLite storage, todo→done move

current_version = "20260526-113507"

import argparse
import base64
import json
import logging
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import anthropic

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_TODO = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\kassabonnen\todo"
DEFAULT_DONE = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\kassabonnen\done"
DEFAULT_DB   = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\kassabonnen\receipts.db"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif"}

MEDIA_TYPE_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
    ".bmp":  "image/png",   # Claude doesn't support bmp natively; caller should convert
    ".tiff": "image/png",
    ".tif":  "image/png",
}

SYSTEM_PROMPT = """You are a receipt parser. Extract all purchased line items from the receipt image.

Return ONLY a JSON object — no markdown, no explanation, no backticks.

...

Rules:
- Skip non-product lines: store name, address, date/time, subtotals, totals, 
  payment lines, VAT summaries, card info.
- ALWAYS skip lines containing these Dutch keywords (case-insensitive):
  Koopsom, Totaal, Subtotaal, Bruto, Netto, BTW, Kaart, KaartNr, Betaling,
  Betalingsmethode, Wisselgeld, Korting (unless it's a product discount),
  Aantal (as a summary line), Kassabon, Datum, Tijd, Bon, Referentie.
- Discount lines (e.g. "Actieprijs -0,40") must be merged into the preceding 
  product — do NOT emit a separate row.
...
"""

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Database ─────────────────────────────────────────────────────────────────

def init_db(db_path: Path) -> sqlite3.Connection:
    """Create (or open) the SQLite database and ensure tables exist."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS receipts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            filename      TEXT    NOT NULL UNIQUE,
            original_path TEXT    NOT NULL,
            done_path     TEXT,
            store         TEXT,
            receipt_date  TEXT,
            currency      TEXT    DEFAULT 'EUR',
            item_count    INTEGER DEFAULT 0,
            total_amount  REAL    DEFAULT 0,
            processed_at  TEXT    NOT NULL,
            status        TEXT    NOT NULL DEFAULT 'ok',   -- 'ok' | 'error'
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS receipt_items (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id    INTEGER NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
            description   TEXT    NOT NULL,
            quantity      REAL    NOT NULL DEFAULT 1,
            unit_price    REAL,
            total_price   REAL,
            tax_category  TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_items_receipt ON receipt_items(receipt_id);
    """)
    conn.commit()
    return conn


def insert_receipt(
    conn: sqlite3.Connection,
    filename: str,
    original_path: str,
    done_path: str | None,
    parsed: dict | None,
    status: str,
    error_message: str | None,
) -> int:
    """Insert a receipt record and its items. Returns the new receipt id."""
    items = parsed.get("items", []) if parsed else []
    total = sum(float(i.get("total_price") or 0) for i in items)

    cur = conn.execute(
        """
        INSERT INTO receipts
            (filename, original_path, done_path, store, receipt_date, currency,
             item_count, total_amount, processed_at, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            filename,
            original_path,
            done_path,
            parsed.get("store", "") if parsed else None,
            parsed.get("date", "") if parsed else None,
            parsed.get("currency", "EUR") if parsed else None,
            len(items),
            round(total, 2),
            datetime.now(timezone.utc).isoformat(),
            status,
            error_message,
        ),
    )
    receipt_id = cur.lastrowid

    for item in items:
        conn.execute(
            """
            INSERT INTO receipt_items
                (receipt_id, description, quantity, unit_price, total_price, tax_category)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                receipt_id,
                item.get("description", ""),
                float(item.get("quantity") or 1),
                float(item.get("unit_price") or 0),
                float(item.get("total_price") or 0),
                item.get("tax_category", ""),
            ),
        )

    conn.commit()
    return receipt_id

# ── Claude OCR ───────────────────────────────────────────────────────────────

def image_to_base64(path: Path) -> tuple[str, str]:
    """Return (base64_data, media_type)."""
    media_type = MEDIA_TYPE_MAP.get(path.suffix.lower(), "image/jpeg")
    with path.open("rb") as f:
        data = base64.standard_b64encode(f.read()).decode()
    return data, media_type


def parse_receipt_image(client: anthropic.Anthropic, image_path: Path) -> dict:
    """Send one image to Claude and return the parsed receipt dict."""
    img_data, media_type = image_to_base64(image_path)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_data,
                        },
                    },
                    {"type": "text", "text": "Parse this supermarket receipt."},
                ],
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)

# ── Main pipeline ─────────────────────────────────────────────────────────────

def already_processed(conn: sqlite3.Connection, filename: str) -> bool:
    """Return True if this filename is already in the DB with status='ok'."""
    row = conn.execute(
        "SELECT status FROM receipts WHERE filename = ?", (filename,)
    ).fetchone()
    return row is not None and row["status"] == "ok"


def process_folder(todo_dir: Path, done_dir: Path, db_path: Path) -> None:
    done_dir.mkdir(parents=True, exist_ok=True)

    images = [
        p for p in sorted(todo_dir.iterdir())
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    
    if not images:
        log.info("No image files found in %s", todo_dir)
        return

    log.info("Found %d image(s) in %s", len(images), todo_dir)

    conn = init_db(db_path)
    client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from environment

    ok_count = skipped_count = error_count = 0

    iterator = tqdm(images, desc="Receipts", unit=" img", dynamic_ncols=True) if HAS_TQDM else images

    for img_path in iterator:
        filename = img_path.name

        if already_processed(conn, filename):
            log.info("SKIP  %s  (already in DB)", filename)
            skipped_count += 1
            continue

        log.info("OCR   %s", filename)
        done_path: Path | None = None
        parsed: dict | None = None
        status = "ok"
        error_message: str | None = None

        try:
            parsed = parse_receipt_image(client, img_path)
        except Exception as exc:
            status = "error"
            error_message = str(exc)
            log.error("      → OCR failed: %s", exc)
            error_count += 1

        # Move file to done/ regardless of OCR success so we don't retry corrupt files
        try:
            dest = done_dir / filename
            # If a file with the same name already exists in done/, suffix it
            if dest.exists():
                stem = img_path.stem
                suffix = img_path.suffix
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                dest = done_dir / f"{stem}_{ts}{suffix}"
            shutil.move(str(img_path), dest)
            done_path = dest
            log.info("      → moved to %s", dest)
        except Exception as exc:
            log.warning("      → could not move file: %s", exc)

        insert_receipt(
            conn,
            filename=filename,
            original_path=str(img_path),
            done_path=str(done_path) if done_path else None,
            parsed=parsed,
            status=status,
            error_message=error_message,
        )

        if status == "ok":
            item_count = len(parsed.get("items", [])) if parsed else 0
            total = sum(float(i.get("total_price") or 0) for i in (parsed or {}).get("items", []))
            log.info("      → %d items, total %.2f %s",
                     item_count, total, (parsed or {}).get("currency", "EUR"))
            ok_count += 1

    conn.close()

    log.info("")
    log.info("Done. OK: %d  |  Skipped: %d  |  Errors: %d", ok_count, skipped_count, error_count)
    log.info("Database: %s", db_path)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch-OCR supermarket receipts with Claude and store results in SQLite."
    )
    parser.add_argument("--todo", default=DEFAULT_TODO,
                        help=f"Folder with receipt images to process (default: {DEFAULT_TODO})")
    parser.add_argument("--done", default=DEFAULT_DONE,
                        help=f"Folder to move processed images to (default: {DEFAULT_DONE})")
    parser.add_argument("--db",   default=DEFAULT_DB,
                        help=f"SQLite database path (default: {DEFAULT_DB})")
    args = parser.parse_args()

    process_folder(
        todo_dir=Path(args.todo),
        done_dir=Path(args.done),
        db_path=Path(args.db),
    )


if __name__ == "__main__":
    main()
