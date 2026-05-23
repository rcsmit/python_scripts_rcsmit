"""
sort_files_by_topic.py

Sorts thousands of files into topic-based subdirectories using Claude AI.
Supports PDF, TXT, RTF, DOC, DOCX, XLS, XLSX, CSV, and image files
(JPG, JPEG, PNG, TIFF, BMP, GIF, WEBP — via Claude Vision API, not OCR).

Files with meaningless names (only digits, UUIDs, random char combos) are
automatically renamed to a descriptive name suggested by Claude — at no
extra API cost, since the rename is included in the same classification call.

Just run:
    python sort_files_by_topic.py              # does everything: submit -> wait -> collect
    python sort_files_by_topic.py --dry-run    # preview without moving files
    python sort_files_by_topic.py --standard   # real-time API (no batch, immediate)
    python sort_files_by_topic.py --collect    # manually collect a previously submitted batch
    python sort_files_by_topic.py --wait       # same as default (explicit)

Override directories if needed:
    python sort_files_by_topic.py --input /other/dir --output /other/sorted

Requirements:
    pip install pdfplumber anthropic tqdm python-docx openpyxl pillow striprtf

    For DOC (legacy Word) support:
        Linux/Mac: sudo apt install antiword  /  brew install antiword

    For image support (resize + format conversion before Vision API):
        pip install pillow --break-system-packages  # required for all image types

Environment:
    ANTHROPIC_API_KEY must be set.

    Mac/Linux:  export ANTHROPIC_API_KEY="sk-ant-..."
    Windows:    set ANTHROPIC_API_KEY=sk-ant-...
    PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."

    Add the export line to ~/.bashrc or ~/.zshrc to make it permanent.
    Never hardcode the key in this file or commit it to Git.

Costs (indicative):
    17/05/2026 : EUR 0.27 for 433 pdfs
    10,000 files ~ EUR 7 with Haiku + Batch API
"""

import argparse
import json
import logging
import os
import random
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

import anthropic
import pdfplumber
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Suppress noisy library loggers (must be before basicConfig)
# ---------------------------------------------------------------------------
for _noisy in (
    "pdfplumber", "pdfminer", "pdfminer.high_level", "pdfminer.layout",
    "pypdf", "pypdf._reader", "pypdf._page", "pypdf.generic",
    "PIL", "PIL.Image",
):
    logging.getLogger(_noisy).setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# *** USER CONFIGURATION — edit these two lines, nothing else is required ***
# ---------------------------------------------------------------------------

# INPUT_DIR:  Path = Path(r"C:\Users\rcxsm\Documents\docx")
# OUTPUT_DIR: Path = Path(r"C:\Users\rcxsm\Documents\docx\sorted")
INPUT_DIR:  Path = Path(r"C:\Users\rcxsm\Pictures\unsorted\to_sort")
OUTPUT_DIR: Path = Path(r"C:\Users\rcxsm\Pictures\unsorted\sorted")

# ---------------------------------------------------------------------------
# Topic list
# ---------------------------------------------------------------------------

DEFAULT_TOPICS: list[str] = [
    "Finance & Accounting",
    "Legal & Contracts",
    "Medical & Health",
    "Technical & Engineering",
    "Science & Research",
    "Business & Management",
    "Education & Training",
    "Government & Policy",
    "Human Resources",
    "Marketing & Sales",
    "Real Estate",
    "Sheet music",
    "Travel & Tourism",
    "Art & Culture",
    "Spiritual & Yoga",
    "Food & Beverage",
    "Service Quality",
    "Bank accounts",
    "Manuals",
    "Persons & groups",
    "Maps",
    "Veganism",
    "Covid",
    "Hospitality & Catering",
    "Other",
]

# ---------------------------------------------------------------------------
# Supported file extensions
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS: set[str] = {
    ".pdf",
    ".txt", ".rtf", ".csv", ".html", ".htm",
    ".doc", ".docx",
    ".xls", ".xlsx",
    ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif", ".webp",
}

# ---------------------------------------------------------------------------
# Technical configuration
# ---------------------------------------------------------------------------

MODEL:               str   = "claude-haiku-4-5-20251001"
PAGES_TO_EXTRACT:    int   = 2        # pages to read per PDF/DOCX
MAX_CHARS_PER_FILE:  int   = 3_000    # max chars sent to Claude per file
BATCH_SIZE:          int   = 10       # files per API request
MAX_WORKERS:         int   = 16       # parallel extraction threads
API_RETRY_ATTEMPTS:  int   = 3
API_RETRY_DELAY:     float = 5.0      # seconds between retries
BATCH_POLL_INTERVAL: int   = 60       # seconds between batch status polls
IMAGE_VISION_BATCH_SIZE: int = 20     # images per Claude Vision API call (max ~20)
INTER_BATCH_DELAY_MIN:  float = 1.0   # min random pause between API calls (seconds)
INTER_BATCH_DELAY_MAX:  float = 3.0   # max random pause between API calls (seconds)
PROGRESS_FILE:       str   = "sort_progress.json"
BATCH_STATE_FILE:    str   = "sort_batch_state.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FileRecord:
    """Metadata, extracted text, and classification result for one file.

    Attributes:
        path:      Absolute path to the file.
        text:      Extracted text snippet.
        topic:     Assigned topic after classification.
        new_name:  Suggested filename stem (without extension) for bad names.
        error:     Error message if extraction or classification failed.
        custom_id: Unique ID correlating batch sub-requests with records.
    """
    path:      Path
    text:      str = ""
    topic:     str = ""
    new_name:  str = ""
    error:     str = ""
    custom_id: str = ""


@dataclass
class SortStats:
    """Running counters for a sorting run.

    Attributes:
        total:        Total files found.
        classified:   Successfully classified.
        moved:        Successfully moved/copied.
        skipped:      Already processed (resume).
        failed:       Extraction or API failures.
        renamed:      Files given a new name by Claude.
        topic_counts: Counter per topic.
        type_counts:  Counter per file extension.
    """
    total:        int = 0
    classified:   int = 0
    moved:        int = 0
    skipped:      int = 0
    failed:       int = 0
    renamed:      int = 0
    topic_counts: dict[str, int] = field(default_factory=dict)
    type_counts:  dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Filename quality check
# ---------------------------------------------------------------------------

def _is_bad_filename(stem: str) -> bool:
    """Return True if the filename stem is meaningless and should be renamed.

    Catches: pure digit strings, UUIDs, random alphanumeric blobs, very short
    consonant-only strings, and names with fewer than 40% letter characters.

    Args:
        stem: Filename without extension.

    Returns:
        True if the name should be replaced with a descriptive one.
    """
    if not stem:
        return True
    if stem.isdigit():
        return True
    if re.fullmatch(
        r"[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}",
        stem, re.I,
    ):
        return True
    letters = sum(c.isalpha() for c in stem)
    if len(stem) >= 4 and letters / len(stem) < 0.4:
        return True
    if len(stem) <= 6 and not any(c in "aeiouAEIOU" for c in stem):
        return True
    return False


def _sanitize_suggested_name(raw: str) -> str:
    """Sanitize a Claude-suggested filename stem to be filesystem-safe.

    Args:
        raw: Raw suggested name from Claude (no extension).

    Returns:
        Alphanumeric + underscore string, max 30 characters.
    """
    cleaned = re.sub(r"[^\w]", "_", raw.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[:30]


# ---------------------------------------------------------------------------
# Text extraction — per file type
# ---------------------------------------------------------------------------

def _extract_pdf(file_path: Path, max_chars: int) -> str:
    with pdfplumber.open(str(file_path)) as pdf:
        chunks = [page.extract_text() or "" for page in pdf.pages[:PAGES_TO_EXTRACT]]
    return "\n".join(chunks).strip()[:max_chars]


def _extract_pdf_pdftotext(file_path: Path, max_chars: int) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", "-l", str(PAGES_TO_EXTRACT), str(file_path), "-"],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip()[:max_chars]
    except FileNotFoundError:
        log.debug("pdftotext not found; falling back to pdfplumber for %s", file_path.name)
        return _extract_pdf(file_path, max_chars)


def _extract_txt(file_path: Path, max_chars: int) -> str:
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return file_path.read_text(encoding=encoding)[:max_chars]
        except UnicodeDecodeError:
            continue
    return ""


def _extract_rtf(file_path: Path, max_chars: int) -> str:
    from striprtf.striprtf import rtf_to_text  # type: ignore
    raw = file_path.read_text(encoding="latin-1")
    return rtf_to_text(raw)[:max_chars]


def _extract_docx(file_path: Path, max_chars: int) -> str:
    import docx  # type: ignore
    doc = docx.Document(str(file_path))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return text[:max_chars]


def _extract_doc(file_path: Path, max_chars: int) -> str:
    try:
        result = subprocess.run(
            ["antiword", str(file_path)],
            capture_output=True, text=True, timeout=15,
        )
        return result.stdout.strip()[:max_chars]
    except FileNotFoundError:
        print("antiword not found; cannot extract .doc: %s", file_path.name)
        log.debug("antiword not found; cannot extract .doc: %s", file_path.name)
        return ""


def _extract_xlsx(file_path: Path, max_chars: int) -> str:
    number_of_sheets = 1
    import openpyxl  # type: ignore
    wb = openpyxl.load_workbook(str(file_path), read_only=True, data_only=True)
    chunks: list[str] = []
    for sheet in wb.worksheets[:number_of_sheets]:
        for row in sheet.iter_rows(max_row=50, values_only=True):
            row_text = "  ".join(str(c) for c in row if c is not None)
            if row_text.strip():
                chunks.append(row_text)
    return "\n".join(chunks)[:max_chars]

def _extract_image_with_pytesseract(file_path: Path, max_chars: int) -> str:
    """ Not used """

    try:
        import pytesseract          # type: ignore
        from PIL import Image       # type: ignore
        img = Image.open(str(file_path))
        return pytesseract.image_to_string(img)[:max_chars]
    except ImportError:
        log.debug("pytesseract/Pillow not installed; skipping OCR for %s", file_path.name)
        return ""
    except Exception as exc:
        log.debug("OCR failed for %s: %s", file_path.name, exc)
        return ""


def _extract_image(file_path: Path, max_chars: int) -> str:
    """Return a sentinel so the pipeline knows this is an image file.

    Images are classified via Claude Vision (not OCR), so we return a
    placeholder that signals the image path.  The actual vision call is made
    in classify_images_standard() / classify_images_batch_inline().
    """
    return f"__IMAGE_FILE__:{file_path}"


# ---------------------------------------------------------------------------
# Image description helpers  (max 50-char prefix + topic in one vision call)
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif", ".webp"}
)

_MEDIA_TYPE_MAP: dict[str, str] = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
    ".tiff": "image/jpeg",   # convert below
    ".tif":  "image/jpeg",
    ".bmp":  "image/jpeg",
}


# Anthropic API rejects images larger than ~5 MB (base64-encoded).
# We resize to fit within this budget using Pillow before encoding.
_MAX_IMAGE_BYTES: int   = 4_500_000   # 4.5 MB base64 budget (conservative)
_MAX_IMAGE_DIM:   int   = 1568        # max long-edge in pixels (good quality, small size)


def _image_to_base64(file_path: Path) -> tuple[str, str]:
    """Return (base64_data, media_type) for an image file.

    All images are processed through Pillow so we can:
      - Resize large images to fit within the API size limit
      - Convert TIFF / BMP (not accepted by the API) to JPEG
      - Re-compress oversized JPEGs iteratively until they fit

    Args:
        file_path: Path to the image file.

    Returns:
        Tuple of (base64-encoded bytes as str, MIME type string).

    Raises:
        ImportError: If Pillow is not installed.
        OSError: If the file cannot be read or converted.
    """
    import base64
    import io
    from PIL import Image as _PILImage  # type: ignore

    img = _PILImage.open(str(file_path)).convert("RGB")

    # Resize if the long edge exceeds the limit
    w, h = img.size
    long_edge = max(w, h)
    if long_edge > _MAX_IMAGE_DIM:
        scale = _MAX_IMAGE_DIM / long_edge
        img = img.resize((int(w * scale), int(h * scale)), _PILImage.LANCZOS)

    # Encode to JPEG and iteratively reduce quality until size fits
    quality = 85
    while quality >= 30:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        encoded = base64.b64encode(buf.getvalue()).decode()
        if len(encoded) <= _MAX_IMAGE_BYTES:
            return encoded, "image/jpeg"
        quality -= 10

    # Last resort: halve the resolution once more
    img = img.resize((img.width // 2, img.height // 2), _PILImage.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=60)
    return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"


def _vision_classify_batch(
    client: anthropic.Anthropic,
    records: list["FileRecord"],
    topics: list[str],
    retries: int,
    retry_delay: float,
) -> None:
    """Classify a batch of image FileRecords via Claude Vision in one API call.

    Sends all images in a single multi-image message.  Each image gets:
      - A topic from the allowed list
      - A short_description (≤50 chars, plain language, no quotes) that is used
        as a filename prefix when the original filename is meaningless.

    Results are written back into each record's .topic and .new_name fields.

    Args:
        client:      Anthropic client.
        records:     Image FileRecords whose .text starts with '__IMAGE_FILE__:'.
        topics:      Allowed topic strings.
        retries:     Number of retry attempts on API failure.
        retry_delay: Seconds to wait between retries.
    """
    if not records:
        return

    topic_list = "\n".join(f"- {t}" for t in topics)
    content: list[dict] = []

    # Build multi-image message
    for i, record in enumerate(records):
        try:
            b64, media_type = _image_to_base64(record.path)
        except Exception as exc:
            log.warning("Cannot encode image %s: %s", record.path.name, exc)
            record.error = "image_encode_failed"
            record.topic = "Other"
            continue

        content.append({
            "type": "text",
            "text": (
                f"Image {i} — filename: {record.path.name}"
                + ("  [NEEDS_RENAME]" if _is_bad_filename(record.path.stem) else "")
            ),
        })
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64},
        })

    content.append({
        "type": "text",
        "text": (
            "You are an image classifier.\n\n"
            f"Allowed topics:\n{topic_list}\n\n"
            "For EACH image above return a JSON object with:\n"
            '  "index"             : integer (same order as shown above)\n'
            '  "topic"             : exactly one topic from the allowed list\n'
            '  "short_description" : max 50 characters, plain language description of '
            "what the image shows — always required for every image. "
            "No quotes, no special chars, lowercase, suitable as a filename prefix "
            "(e.g. 'sunset over amsterdam canal', 'dog playing in snow').\n\n"
            "Return ONLY a JSON array — no markdown, no explanation.\n"
            "Example: "
            '[{"index":0,"topic":"Travel & Tourism","short_description":"sunset over amsterdam canal"}]'
        ),
    })

    for attempt in range(1, retries + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=512,
                messages=[{"role": "user", "content": content}],
            )
            raw = ""
            if response.content and hasattr(response.content[0], "text"):
                raw = response.content[0].text

            if not raw:
                log.warning("Vision classify attempt %d/%d: empty response.", attempt, retries)
                if attempt < retries:
                    time.sleep(retry_delay)
                continue

            try:
                results = _extract_json_array(raw)
            except (ValueError, json.JSONDecodeError) as exc:
                log.warning("Vision parse attempt %d/%d: %s", attempt, retries, exc)
                if attempt < retries:
                    time.sleep(retry_delay)
                continue

            for item in results:
                if not isinstance(item, dict):
                    continue
                try:
                    idx = int(item["index"])
                except (KeyError, ValueError, TypeError):
                    continue
                if idx < 0 or idx >= len(records):
                    continue

                topic = str(item.get("topic", "")).strip()
                if not topic:
                    topic = "Other"
                elif topic not in topics:
                    topic = _best_match(topic, topics)
                records[idx].topic = topic

                desc = item.get("short_description", "")
                if desc:
                    clean_desc = _sanitize_suggested_name(str(desc))
                    orig_stem  = records[idx].path.stem
                    if _is_bad_filename(orig_stem):
                        # Bad name: replace entirely with description
                        records[idx].new_name = clean_desc[:50]
                    else:
                        # Good name: prepend description as prefix
                        records[idx].new_name = f"{clean_desc[:30]}_{orig_stem}"[:80]

            # Fill in any records that didn't get a result
            for record in records:
                if not record.topic:
                    record.topic = "Other"
            return

        except anthropic.RateLimitError:
            log.warning(
                "Rate limited on vision call; waiting %.0fs (attempt %d/%d)",
                retry_delay * 2, attempt, retries,
            )
            time.sleep(retry_delay * 2)
        except anthropic.APIStatusError as exc:
            log.warning("Vision API error %s attempt %d/%d", exc.status_code, attempt, retries)
            time.sleep(retry_delay)
        if attempt < retries:
            time.sleep(retry_delay)

    for record in records:
        if not record.topic:
            record.error = "classification_failed"
            record.topic = "Other"


def extract_text_from_file(file_path: Path, max_chars: int) -> str:
    """Dispatch text extraction to the correct handler based on file extension."""
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _extract_pdf(file_path, max_chars)
        elif suffix in (".txt", ".csv", ".htm", ".html"):
            return _extract_txt(file_path, max_chars)
        elif suffix == ".rtf":
            return _extract_rtf(file_path, max_chars)
        elif suffix == ".docx":
            return _extract_docx(file_path, max_chars)
        elif suffix == ".doc":
            return _extract_doc(file_path, max_chars)
        elif suffix in (".xlsx", ".xls"):
            return _extract_xlsx(file_path, max_chars)
        elif suffix in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif", ".webp"):
            return _extract_image(file_path, max_chars)
    except Exception as exc:
        log.debug("Extraction failed for %s: %s", file_path.name, exc)
    return ""


# ---------------------------------------------------------------------------
# Parallel extraction
# ---------------------------------------------------------------------------

def extract_texts_parallel(records: list[FileRecord], max_chars: int, workers: int) -> None:
    """Fill FileRecord.text for each record in-place using a thread pool."""
    def _extract(record: FileRecord) -> None:
        record.text = extract_text_from_file(record.path, max_chars)
        if not record.text:
            record.error = "empty_text"

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_extract, r): r for r in records}
        for future in tqdm(as_completed(futures), total=len(futures),
                           desc="Extracting text", unit="file"):
            future.result()


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_classification_prompt(batch: list[FileRecord], topics: list[str]) -> str:
    """Build the classification prompt, requesting a suggested name for bad filenames."""
    topic_list = "\n".join(f"- {t}" for t in topics)
    needs_rename = any(_is_bad_filename(r.path.stem) for r in batch)

    entries: list[str] = []
    for i, record in enumerate(batch):
        snippet = record.text if record.text else "(no text extracted)"
        ext     = record.path.suffix.upper()
        tag     = " [NEEDS_RENAME]" if _is_bad_filename(record.path.stem) else ""
        entries.append(f"### File {i} [{ext}]{tag}\nFilename: {record.path.name}\n\n{snippet}")
    docs_block = "\n\n".join(entries)

    rename_instruction = (
        '\nFor files marked [NEEDS_RENAME], also include a "suggested_name" key: '
        "a descriptive filename stem of max 30 characters, no extension, "
        'use_underscores_for_spaces, no special characters. Omit "suggested_name" for other files.\n'
    ) if needs_rename else ""

    return (
        "You are a document classifier. Assign exactly one topic from the list below to each file.\n\n"
        f"Allowed topics:\n{topic_list}\n\n"
        f"{rename_instruction}"
        'Return ONLY a JSON array — one object per file in the same order provided.\n'
        'Required keys: "index" (integer), "topic" (string from list above).\n'
        'Optional key:  "suggested_name" (string, only for [NEEDS_RENAME] files).\n'
        "No explanation, no markdown — only raw JSON.\n\n"
        f"Files to classify:\n\n{docs_block}\n"
    )


# ---------------------------------------------------------------------------
# JSON extraction helper
# ---------------------------------------------------------------------------

def _extract_json_array(raw: str) -> list[dict]:
    """Robustly extract a JSON array from Claude's response.

    Handles: raw JSON, ```json fences, leading/trailing prose, partial wrapping.

    Args:
        raw: Raw text from Claude.

    Returns:
        Parsed list of dicts.

    Raises:
        ValueError: If no valid JSON array can be extracted.
    """
    text = raw.strip()

    # Strip ```json ... ``` fences
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("["):
                text = candidate
                break

    # Try the whole string first
    if text.startswith("["):
        try:
            result = json.loads(text)
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # Find the first '[' ... last ']' bracket pair
    start = text.find("[")
    end   = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            result = json.loads(text[start : end + 1])
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON array found in response (length {len(raw)}): {raw[:200]!r}")


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

def _parse_classification_response(
    raw: str,
    batch: list[FileRecord],
    topics: list[str],
) -> bool:
    """Parse Claude's JSON response and populate batch records in-place.

    Args:
        raw:    Raw text response from Claude.
        batch:  Records to populate with topic and new_name.
        topics: Allowed topic strings for validation.

    Returns:
        True if parsing succeeded; False if the response was unparseable.
    """
    try:
        results = _extract_json_array(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        log.warning("Could not parse classification response: %s", exc)
        return False

    if not isinstance(results, list) or not results:
        log.warning("Classification response is not a non-empty list.")
        return False

    parsed_count = 0
    for item in results:
        if not isinstance(item, dict):
            log.warning("Skipping non-dict item in classification response: %r", item)
            continue
        try:
            idx: int = int(item["index"])
        except (KeyError, ValueError, TypeError):
            log.warning("Skipping item with missing/bad 'index': %r", item)
            continue
        if idx < 0 or idx >= len(batch):
            log.warning("Index %d out of range for batch of size %d; skipping.", idx, len(batch))
            continue

        topic = str(item.get("topic", "")).strip()
        if not topic:
            log.warning("Empty topic for index %d; defaulting to 'Other'.", idx)
            topic = "Other"
        elif topic not in topics:
            topic = _best_match(topic, topics)

        batch[idx].topic = topic

        suggested = item.get("suggested_name")
        if suggested:
            batch[idx].new_name = _sanitize_suggested_name(str(suggested))

        parsed_count += 1

    if parsed_count == 0:
        log.warning("Classification response parsed 0 valid items.")
        return False

    return True


def _best_match(topic: str, allowed: list[str]) -> str:
    """Return the best-matching allowed topic via case-insensitive substring."""
    topic_lower = topic.lower()
    for candidate in allowed:
        if topic_lower in candidate.lower() or candidate.lower() in topic_lower:
            return candidate
    return "Other"


# ---------------------------------------------------------------------------
# Standard (real-time) classification
# ---------------------------------------------------------------------------

def classify_batch_standard(
    client: anthropic.Anthropic,
    batch: list[FileRecord],
    topics: list[str],
    retries: int,
    retry_delay: float,
) -> None:
    """Classify a batch via the synchronous Messages API."""
    prompt = build_classification_prompt(batch, topics)

    for attempt in range(1, retries + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = ""
            if response.content and hasattr(response.content[0], "text"):
                raw = response.content[0].text
            if raw and _parse_classification_response(raw, batch, topics):
                return
            log.warning("Classify attempt %d/%d: empty or unparseable response.", attempt, retries)
        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
            log.warning("Parse error attempt %d/%d: %s", attempt, retries, exc)
        except anthropic.RateLimitError:
            log.warning("Rate limited; waiting %.0fs (attempt %d/%d)", retry_delay * 2, attempt, retries)
            time.sleep(retry_delay * 2)
        except anthropic.APIStatusError as exc:
            log.warning("API error %s attempt %d/%d", exc.status_code, attempt, retries)
            time.sleep(retry_delay)
        if attempt < retries:
            time.sleep(retry_delay)

    for record in batch:
        if not record.topic:
            record.error = "classification_failed"
            record.topic = "Other"


# ---------------------------------------------------------------------------
# Batch API — submit
# ---------------------------------------------------------------------------

def build_batch_requests(
    all_records: list[FileRecord],
    topics: list[str],
    batch_size: int,
) -> list[dict]:
    """Build Batch API request dicts; assign custom_ids to all records."""
    requests: list[dict] = []
    sub_batches = [all_records[i: i + batch_size] for i in range(0, len(all_records), batch_size)]
    for sub_idx, sub_batch in enumerate(sub_batches):
        for rec_idx, record in enumerate(sub_batch):
            record.custom_id = f"sub{sub_idx:06d}_rec{rec_idx:04d}"
        prompt = build_classification_prompt(sub_batch, topics)
        requests.append({
            "custom_id": f"sub{sub_idx:06d}",
            "params": {
                "model": MODEL,
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}],
            },
        })
    return requests


def submit_batch(
    client: anthropic.Anthropic,
    all_records: list[FileRecord],
    topics: list[str],
    batch_size: int,
    state_path: Path,
) -> str:
    """Submit all requests to the Batch API and save state for collect phase."""
    log.info("Building batch requests…")
    requests = build_batch_requests(all_records, topics, batch_size)
    log.info("Submitting %d requests to Batch API…", len(requests))

    response  = client.beta.messages.batches.create(requests=requests)
    batch_id: str = response.id
    log.info("Batch submitted. ID: %s  |  Status: %s", batch_id, response.processing_status)

    id_to_path: dict[str, str] = {
        record.custom_id: str(record.path.resolve()) for record in all_records
    }
    state = {"batch_id": batch_id, "topics": topics, "batch_size": batch_size, "id_to_path": id_to_path}
    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
    log.info("Batch state saved to %s", state_path)
    return batch_id


# ---------------------------------------------------------------------------
# Batch API — collect
# ---------------------------------------------------------------------------

def poll_batch_until_done(client: anthropic.Anthropic, batch_id: str, poll_interval: int) -> None:
    """Block until the batch reaches the 'ended' status."""
    log.info("Polling batch %s every %ds…", batch_id, poll_interval)
    while True:
        batch  = client.beta.messages.batches.retrieve(batch_id)
        status = batch.processing_status
        counts = batch.request_counts
        log.info(
            "Status: %-12s  processing=%d  succeeded=%d  errored=%d",
            status, counts.processing, counts.succeeded, counts.errored,
        )
        if status == "ended":
            break
        time.sleep(poll_interval)
    log.info("Batch %s finished.", batch_id)


def collect_batch_results(
    client: anthropic.Anthropic,
    batch_id: str,
    topics: list[str],
    id_to_path: dict[str, str],
    batch_size: int,
) -> dict[str, tuple[str, str]]:
    """Retrieve batch results; return path → (topic, new_name) mapping."""
    # Reconstruct sub-batch structure
    sub_batches: dict[int, list[tuple[int, str, str]]] = {}
    for custom_id, abs_path in id_to_path.items():
        try:
            parts   = custom_id.split("_")
            sub_idx = int(parts[0][3:])
            rec_idx = int(parts[1][3:])
        except (IndexError, ValueError):
            log.warning("Malformed custom_id %r in state file; skipping.", custom_id)
            continue
        sub_batches.setdefault(sub_idx, []).append((rec_idx, custom_id, abs_path))

    ordered: dict[int, list[tuple[int, str, str]]] = {
        k: sorted(v, key=lambda x: x[0]) for k, v in sub_batches.items()
    }

    path_to_result: dict[str, tuple[str, str]] = {}
    result_count = 0
    log.info("Streaming batch results for %s…", batch_id)

    for result in client.beta.messages.batches.results(batch_id):
        sub_id  = result.custom_id
        try:
            sub_idx = int(sub_id[3:])
        except (ValueError, IndexError):
            log.warning("Malformed sub_id %r in batch results; skipping.", sub_id)
            continue

        if result.result.type != "succeeded":
            log.warning("Sub-batch %s failed: %s", sub_id, result.result.type)
            for _, _, path in ordered.get(sub_idx, []):
                path_to_result[path] = ("Other", "")
            continue

        # Safely extract text from response
        raw = ""
        try:
            content = result.result.message.content
            if content and hasattr(content[0], "text"):
                raw = content[0].text
        except (AttributeError, IndexError, TypeError) as exc:
            log.warning("Could not read content from sub-batch %s: %s", sub_id, exc)

        sub_entries  = ordered.get(sub_idx, [])
        stub_records = [FileRecord(path=Path(p), custom_id=cid) for _, cid, p in sub_entries]

        if not raw:
            log.warning("Empty response for sub-batch %s; defaulting all to 'Other'.", sub_id)
            for record in stub_records:
                path_to_result[str(record.path.resolve())] = ("Other", "")
            continue

        success = _parse_classification_response(raw, stub_records, topics)
        if not success:
            log.warning("Parse failed for sub-batch %s; defaulting all to 'Other'.", sub_id)

        for record in stub_records:
            # topic is "" if parse failed for that record — fall back to "Other"
            topic = record.topic if record.topic else "Other"
            path_to_result[str(record.path.resolve())] = (topic, record.new_name)
            result_count += 1

    log.info("Collected results for %d files.", result_count)
    return path_to_result


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def sanitize_folder_name(topic: str) -> str:
    """Convert a topic string to a filesystem-safe directory name."""
    for ch in r'/\:*?"<>|&':
        topic = topic.replace(ch, "_")
    return topic.strip().strip(".")


def move_or_copy_file(
    record: FileRecord,
    output_dir: Path,
    copy: bool,
    dry_run: bool,
) -> bool:
    """Move or copy a file into its topic subfolder, applying rename if set."""
    folder_name = sanitize_folder_name(record.topic)
    dest_dir    = output_dir / folder_name

    filename  = (record.new_name + record.path.suffix) if record.new_name else record.path.name
    dest_path = dest_dir / filename

    if dest_path.exists() and not dry_run:
        stem    = Path(filename).stem
        suffix  = record.path.suffix
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter  += 1

    if dry_run:
        action      = "COPY" if copy else "MOVE"
        rename_note = f" → {filename}" if record.new_name else ""
        log.debug("%s [DRY-RUN] %s%s -> %s/", action, record.path.name, rename_note, folder_name)
        return True

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if copy:
            shutil.copy2(str(record.path), str(dest_path))
        else:
            shutil.move(str(record.path), str(dest_path))
        return True
    except OSError as exc:
        log.error("Failed to %s %s: %s", "copy" if copy else "move", record.path.name, exc)
        return False


def apply_topics_and_move(
    path_to_result: dict[str, tuple[str, str]],
    output_dir: Path,
    copy: bool,
    dry_run: bool,
    done: dict[str, str],
    progress_path: Path,
) -> SortStats:
    """Move/copy all files based on path→(topic, new_name); update progress."""
    stats       = SortStats()
    stats.total = len(path_to_result)

    for abs_path_str, (topic, new_name) in tqdm(
        path_to_result.items(), desc="Moving files", unit="file"
    ):
        record  = FileRecord(path=Path(abs_path_str), topic=topic, new_name=new_name)
        success = move_or_copy_file(record, output_dir, copy=copy, dry_run=dry_run)
        if success:
            stats.moved      += 1
            stats.classified += 1
            if new_name:
                stats.renamed += 1
            stats.topic_counts[topic]                    = stats.topic_counts.get(topic, 0) + 1
            ext                                          = record.path.suffix.lower()
            stats.type_counts[ext]                       = stats.type_counts.get(ext, 0) + 1
            if not dry_run:
                done[abs_path_str] = topic
        else:
            stats.failed += 1

        if not dry_run and stats.moved % 50 == 0:
            save_progress(progress_path, done)

    if not dry_run:
        save_progress(progress_path, done)

    return stats


# ---------------------------------------------------------------------------
# Progress / resume
# ---------------------------------------------------------------------------

def load_progress(progress_path: Path) -> dict[str, str]:
    """Load previously completed path→topic mappings from disk."""
    if progress_path.exists():
        try:
            with open(progress_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return data
            log.warning("Progress file has unexpected format; starting fresh.")
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("Could not read progress file (%s); starting fresh.", exc)
    return {}


def save_progress(progress_path: Path, done: dict[str, str]) -> None:
    """Persist completed path→topic mappings to disk."""
    try:
        with open(progress_path, "w", encoding="utf-8") as fh:
            json.dump(done, fh, indent=2)
    except OSError as exc:
        log.warning("Could not save progress: %s", exc)


def load_batch_state(state_path: Path) -> dict:
    """Load the batch state file written during the submit phase.

    Args:
        state_path: Path to the batch state JSON file.

    Returns:
        Dict with keys: batch_id, topics, batch_size, id_to_path.

    Raises:
        FileNotFoundError: If the state file does not exist.
        ValueError: If the file contains invalid JSON or unexpected structure.
        OSError: If the file cannot be read.
    """
    if not state_path.exists():
        raise FileNotFoundError(
            f"Batch state file not found: {state_path}\n"
            "  → Run submit phase first (without --collect)."
        )
    try:
        with open(state_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Batch state file contains invalid JSON: {exc}") from exc
    except OSError as exc:
        raise OSError(f"Could not read batch state file: {exc}") from exc

    # Validate required keys so callers don't get surprise KeyErrors later
    required = {"batch_id", "topics", "batch_size", "id_to_path"}
    missing  = required - data.keys()
    if missing:
        raise ValueError(
            f"Batch state file is missing required keys: {', '.join(sorted(missing))}"
        )
    if not isinstance(data["batch_id"], str) or not data["batch_id"]:
        raise ValueError("Batch state 'batch_id' is empty or not a string.")
    if not isinstance(data["topics"], list):
        raise ValueError("Batch state 'topics' must be a list.")
    if not isinstance(data["id_to_path"], dict):
        raise ValueError("Batch state 'id_to_path' must be a dict.")

    return data


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def collect_files(input_dir: Path) -> list[Path]:
    """Recursively find all supported files under input_dir."""
    return sorted(
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------

def run_standard_pipeline(
    input_dir: Path,
    output_dir: Path,
    topics: list[str],
    dry_run: bool,
    copy: bool,
    batch_size: int,
    workers: int,
) -> SortStats:
    """Standard pipeline: discover → extract → classify (real-time) → move."""
    stats  = SortStats()
    client = _get_client()

    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = output_dir / PROGRESS_FILE
    done: dict[str, str] = {} if dry_run else load_progress(progress_path)

    all_files   = collect_files(input_dir)
    stats.total = len(all_files)
    log.info("Found %d supported files in %s", stats.total, input_dir)

    pending: list[FileRecord] = []
    for fp in all_files:
        key = str(fp.resolve())
        if key in done:
            stats.skipped += 1
        else:
            pending.append(FileRecord(path=fp))

    log.info("%d pending  |  %d skipped (already done)", len(pending), stats.skipped)
    if not pending:
        log.info("Nothing to do.")
        return stats

    # Split early: images use Vision API, text files use text extraction + classify
    image_records = [r for r in pending if r.path.suffix.lower() in IMAGE_EXTENSIONS]
    text_records  = [r for r in pending if r.path.suffix.lower() not in IMAGE_EXTENSIONS]

    if text_records:
        log.info("Extracting text from %d files using %d threads…", len(text_records), workers)
        extract_texts_parallel(text_records, MAX_CHARS_PER_FILE, workers)
    if image_records:
        log.info("Skipping text extraction for %d image files — using Claude Vision instead.", len(image_records))

    # Classify text-based files
    if text_records:
        batches = [text_records[i: i + batch_size] for i in range(0, len(text_records), batch_size)]
        log.info("Classifying %d text batches via standard API…", len(batches))
        for i, batch in enumerate(tqdm(batches, desc="Classifying text", unit="batch")):
            classify_batch_standard(client, batch, topics, API_RETRY_ATTEMPTS, API_RETRY_DELAY)
            stats.classified += sum(1 for r in batch if r.topic and r.error != "classification_failed")
            stats.failed     += sum(1 for r in batch if r.error == "classification_failed")
            if i < len(batches) - 1:
                time.sleep(random.uniform(INTER_BATCH_DELAY_MIN, INTER_BATCH_DELAY_MAX))

    # Classify images via Claude Vision (real-time, batches of IMAGE_VISION_BATCH_SIZE)
    if image_records:
        img_batches = [
            image_records[i: i + IMAGE_VISION_BATCH_SIZE]
            for i in range(0, len(image_records), IMAGE_VISION_BATCH_SIZE)
        ]
        log.info(
            "Classifying %d images in %d vision batches (batch size %d)…",
            len(image_records), len(img_batches), IMAGE_VISION_BATCH_SIZE,
        )
        for i, img_batch in enumerate(tqdm(img_batches, desc="Classifying images", unit="batch")):
            _vision_classify_batch(client, img_batch, topics, API_RETRY_ATTEMPTS, API_RETRY_DELAY)
            stats.classified += sum(1 for r in img_batch if r.topic and r.error != "classification_failed")
            stats.failed     += sum(1 for r in img_batch if r.error == "classification_failed")
            if i < len(img_batches) - 1:
                time.sleep(random.uniform(INTER_BATCH_DELAY_MIN, INTER_BATCH_DELAY_MAX))

    log.info("Moving files%s…", " [DRY-RUN]" if dry_run else "")
    for record in tqdm(pending, desc="Moving files", unit="file"):
        if not record.topic:
            stats.failed += 1
            continue
        success = move_or_copy_file(record, output_dir, copy=copy, dry_run=dry_run)
        if success:
            stats.moved += 1
            if record.new_name:
                stats.renamed += 1
            stats.topic_counts[record.topic] = stats.topic_counts.get(record.topic, 0) + 1
            ext = record.path.suffix.lower()
            stats.type_counts[ext] = stats.type_counts.get(ext, 0) + 1
            if not dry_run:
                done[str(record.path.resolve())] = record.topic
        else:
            stats.failed += 1
        if not dry_run and stats.moved % 50 == 0:
            save_progress(progress_path, done)

    if not dry_run:
        save_progress(progress_path, done)
    return stats


def run_batch_submit_phase(
    input_dir: Path,
    output_dir: Path,
    topics: list[str],
    batch_size: int,
    workers: int,
    dry_run: bool = False,
) -> str:
    """Batch phase 1: extract text, classify images via Vision, submit text files to Batch API."""
    client = _get_client()
    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = output_dir / PROGRESS_FILE
    state_path    = output_dir / BATCH_STATE_FILE
    done          = load_progress(progress_path)

    all_files = collect_files(input_dir)
    log.info("Found %d supported files.", len(all_files))

    pending: list[FileRecord] = []
    skipped = 0
    for fp in all_files:
        key = str(fp.resolve())
        if key in done:
            skipped += 1
        else:
            pending.append(FileRecord(path=fp))

    log.info("%d pending  |  %d skipped (already done)", len(pending), skipped)
    if not pending:
        log.info("Nothing to submit.")
        return ""

    # Split early: images use Vision API, text files use text extraction + batch
    image_records = [r for r in pending if r.path.suffix.lower() in IMAGE_EXTENSIONS]
    text_records  = [r for r in pending if r.path.suffix.lower() not in IMAGE_EXTENSIONS]

    if text_records:
        log.info("Extracting text from %d files using %d threads…", len(text_records), workers)
        extract_texts_parallel(text_records, MAX_CHARS_PER_FILE, workers)
    if image_records:
        log.info("Skipping text extraction for %d image files — using Claude Vision instead.", len(image_records))

    # Images cannot go through the Batch API (no vision support there).
    # Classify them now via real-time Vision API, then exclude from batch submit.
    if image_records:
        img_batches = [
            image_records[i: i + IMAGE_VISION_BATCH_SIZE]
            for i in range(0, len(image_records), IMAGE_VISION_BATCH_SIZE)
        ]
        log.info(
            "Classifying %d images via Vision API (%d batches) before batch submit…",
            len(image_records), len(img_batches),
        )
        for i, img_batch in enumerate(tqdm(img_batches, desc="Classifying images", unit="batch")):
            _vision_classify_batch(client, img_batch, topics, API_RETRY_ATTEMPTS, API_RETRY_DELAY)
            if i < len(img_batches) - 1:
                time.sleep(random.uniform(INTER_BATCH_DELAY_MIN, INTER_BATCH_DELAY_MAX))

        # Apply moves for images right away (can't defer to collect phase)
        img_moved = 0
        img_renamed = 0
        for r in image_records:
            if not r.topic:
                r.topic = "Other"
            success = move_or_copy_file(r, output_dir, copy=dry_run, dry_run=dry_run)
            if success:
                img_moved += 1
                if r.new_name:
                    img_renamed += 1

        # Persist image results + stats so collect phase can include them in summary
        img_result: dict[str, str] = {
            str(r.path.resolve()): r.topic or "Other" for r in image_records
        }
        done.update(img_result)
        # Store image stats under a reserved key for the collect phase
        done["__image_stats__"] = f"{img_moved},{img_renamed}"
        save_progress(progress_path, done)
        log.info(
            "Images: %d moved, %d renamed. Results saved to progress file.",
            img_moved, img_renamed,
        )

    if not text_records:
        log.info("No text-based files to batch-submit.")
        return ""

    batch_id = submit_batch(client, text_records, topics, batch_size, state_path)
    log.info(
        "\nBatch submitted! Wait for it to finish (minutes to ~1 hour), then run:\n"
        "  python sort_files_by_topic.py --collect",
    )
    return batch_id


def run_batch_collect_phase(output_dir: Path, copy: bool, dry_run: bool, wait: bool) -> SortStats:
    """Batch phase 2: retrieve results and move files.

    Returns:
        SortStats with move counts, or empty SortStats if batch not yet done or state missing.
    """
    client     = _get_client()
    state_path = output_dir / BATCH_STATE_FILE

    try:
        state = load_batch_state(state_path)
    except FileNotFoundError as exc:
        log.error("%s", exc)
        return SortStats()
    except (ValueError, OSError) as exc:
        log.error("Failed to load batch state: %s", exc)
        return SortStats()

    batch_id:   str            = state["batch_id"]
    topics:     list[str]      = state["topics"]
    batch_size: int            = state["batch_size"]
    id_to_path: dict[str, str] = state["id_to_path"]

    log.info("Collecting results for batch %s…", batch_id)

    if wait:
        poll_batch_until_done(client, batch_id, BATCH_POLL_INTERVAL)
    else:
        batch_obj = client.beta.messages.batches.retrieve(batch_id)
        if batch_obj.processing_status != "ended":
            log.info(
                "Batch not finished yet (status: %s).\n"
                "Re-run with --collect when it finishes, or use --wait to block.",
                batch_obj.processing_status,
            )
            return SortStats()

    path_to_result = collect_batch_results(client, batch_id, topics, id_to_path, batch_size)

    progress_path = output_dir / PROGRESS_FILE
    done          = load_progress(progress_path)

    # Recover image stats saved during submit phase
    img_stats_raw = done.pop("__image_stats__", "0,0")
    try:
        img_moved, img_renamed = (int(x) for x in img_stats_raw.split(","))
    except ValueError:
        img_moved, img_renamed = 0, 0

    stats = apply_topics_and_move(
        path_to_result=path_to_result,
        output_dir=output_dir,
        copy=copy,
        dry_run=dry_run,
        done=done,
        progress_path=progress_path,
    )

    # Add image counts to summary
    stats.moved      += img_moved
    stats.renamed    += img_renamed
    stats.classified += img_moved
    stats.total      += img_moved

    if not dry_run and state_path.exists():
        state_path.unlink()
        log.info("Batch state file removed.")

    return stats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client() -> anthropic.Anthropic:
    """Create and return an Anthropic client, raising clearly if key is missing."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable is not set.\n"
            "  Mac/Linux:  export ANTHROPIC_API_KEY='sk-ant-...'\n"
            "  Windows:    set ANTHROPIC_API_KEY=sk-ant-...\n"
            "  PowerShell: $env:ANTHROPIC_API_KEY='sk-ant-...'"
        )
    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary(stats: SortStats, dry_run: bool, mode: str) -> None:
    """Print a human-readable summary of the sorting run."""
    tag = " [DRY-RUN]" if dry_run else ""
    print(f"\n{'='*54}")
    print(f"  File Sorting Summary  [{mode.upper()}]{tag}")
    print(f"{'='*54}")
    print(f"  Total files found    :  {stats.total:>6}")
    print(f"  Skipped (done)       :  {stats.skipped:>6}")
    print(f"  Classified           :  {stats.classified:>6}")
    print(f"  Moved/Copied         :  {stats.moved:>6}")
    print(f"  Renamed              :  {stats.renamed:>6}")
    print(f"  Failed               :  {stats.failed:>6}")
    if stats.type_counts:
        print(f"\n  Files processed by type:")
        for ext, count in sorted(stats.type_counts.items(), key=lambda x: -x[1]):
            print(f"    {ext:<12} {count:>5}")
    if stats.topic_counts:
        print(f"\n  Files per topic:")
        for topic, count in sorted(stats.topic_counts.items(), key=lambda x: -x[1]):
            print(f"    {topic:<42} {count:>5}")
    print(f"{'='*54}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Sort files into topic folders using Claude AI.\n"
            f"Edit INPUT_DIR / OUTPUT_DIR at the top of this file, then just run:\n"
            f"  python sort_files_by_topic.py              # batch submit (default)\n"
            f"  python sort_files_by_topic.py --collect    # collect after batch finishes\n"
            f"  python sort_files_by_topic.py --wait       # submit + wait + collect\n"
            f"  python sort_files_by_topic.py --standard   # real-time (no batch)\n"
            f"  python sort_files_by_topic.py --dry-run    # preview\n\n"
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input",  "-i", type=Path, default=None,
                        help=f"Input directory (default: INPUT_DIR = '{INPUT_DIR}').")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help=f"Output directory (default: OUTPUT_DIR = '{OUTPUT_DIR}').")
    parser.add_argument("--topics", "-t", default=None,
                        help="Comma-separated topic labels. Defaults to built-in list.")
    parser.add_argument("--standard",   action="store_true",
                        help="Use real-time standard API instead of batch.")
    parser.add_argument("--collect",    action="store_true",
                        help="Collect batch results and move files (run after submit).")
    parser.add_argument("--wait",       action="store_true",
                        help="Submit (if needed) then block until done and collect automatically.")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE,
                        help=f"Files per API request (default: {BATCH_SIZE}).")
    parser.add_argument("--workers",    type=int, default=MAX_WORKERS,
                        help=f"Parallel extraction threads (default: {MAX_WORKERS}).")
    parser.add_argument("--copy",       action="store_true",
                        help="Copy files instead of moving them.")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Preview without touching any files.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable debug logging.")
    return parser.parse_args()


def _dispatch(args: argparse.Namespace, input_dir: Path, output_dir: Path, topics: list[str]) -> None:
    """Dispatch to the correct pipeline and print summary.

    Extracted so both main_() and main() can share the same dispatch logic
    without duplicating code.
    """
    if args.collect:
        stats = run_batch_collect_phase(
            output_dir=output_dir, copy=args.copy, dry_run=args.dry_run, wait=False,
        )
        print_summary(stats, dry_run=args.dry_run, mode="batch-collect")

    elif args.wait:
        state_path = output_dir / BATCH_STATE_FILE
        if not state_path.exists():
            run_batch_submit_phase(
                input_dir=input_dir, output_dir=output_dir, topics=topics,
                batch_size=args.batch_size, workers=args.workers,
            )
        stats = run_batch_collect_phase(
            output_dir=output_dir, copy=args.copy, dry_run=args.dry_run, wait=True,
        )
        print_summary(stats, dry_run=args.dry_run, mode="batch-wait")

    elif args.standard:
        stats = run_standard_pipeline(
            input_dir=input_dir, output_dir=output_dir, topics=topics,
            dry_run=args.dry_run, copy=args.copy,
            batch_size=args.batch_size, workers=args.workers,
        )
        print_summary(stats, dry_run=args.dry_run, mode="standard")

    else:
        # Default: submit + wait + collect in one run
        state_path = output_dir / BATCH_STATE_FILE
        if not state_path.exists():
            run_batch_submit_phase(
                input_dir=input_dir, output_dir=output_dir, topics=topics,
                batch_size=args.batch_size, workers=args.workers,
            )
        stats = run_batch_collect_phase(
            output_dir=output_dir, copy=args.copy, dry_run=args.dry_run, wait=True,
        )
        print_summary(stats, dry_run=args.dry_run, mode="batch")


def main() -> None:
    """Entry point: parse args, validate, dispatch to correct pipeline."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    input_dir  = (args.input  if args.input  else INPUT_DIR).resolve()
    output_dir = (args.output if args.output else OUTPUT_DIR).resolve()

    if not input_dir.is_dir():
        log.error("Input directory does not exist: %s", input_dir)
        raise SystemExit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    topics: list[str] = (
        [t.strip() for t in args.topics.split(",") if t.strip()]
        if args.topics else DEFAULT_TOPICS
    )

    if args.dry_run:
        log.info("DRY-RUN mode — no files will be moved or copied.")

    log.info("Input  : %s", input_dir)
    log.info("Output : %s", output_dir)
    log.info("Model  : %s", MODEL)
    log.info("Topics (%d): %s", len(topics), ", ".join(topics))

    _dispatch(args, input_dir, output_dir, topics)


def main_loop_file_types() -> None:
    """Loop over file types and run the full pipeline for each."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    topics: list[str] = (
        [t.strip() for t in args.topics.split(",") if t.strip()]
        if args.topics else DEFAULT_TOPICS
    )

    for extension in ["txt", "html", "xls", "pdf", "docx", "img"]:
        print(f"\nStart {extension} : {time.strftime('%H:%M:%S')}")
        start_time_e = int(time.time())

        input_dir  = Path(f"C:\\Users\\rcxsm\\Documents\\{extension}\\unsorted").resolve()
        output_dir = Path(f"C:\\Users\\rcxsm\\Documents\\{extension}\\sorted").resolve()

        if not input_dir.is_dir():
            log.error("Input directory does not exist: %s — skipping %s.", input_dir, extension)
            continue

        output_dir.mkdir(parents=True, exist_ok=True)

        if args.dry_run:
            log.info("DRY-RUN mode — no files will be moved or copied.")

        log.info("Input  : %s", input_dir)
        log.info("Output : %s", output_dir)
        log.info("Model  : %s", MODEL)
        log.info("Topics (%d): %s", len(topics), ", ".join(topics))

        _dispatch(args, input_dir, output_dir, topics)

        elapsed_e            = int(time.time()) - start_time_e
        minutes_e, seconds_e = divmod(elapsed_e, 60)
        print(f"End    : {time.strftime('%H:%M:%S')}")
        print(f"Total time {extension}: {elapsed_e}s  ({minutes_e:02d}:{seconds_e:02d})")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Start : {time.strftime('%H:%M:%S')}")
    start_time = int(time.time())

    main()

    elapsed          = int(time.time()) - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"End   : {time.strftime('%H:%M:%S')}")
    print(f"Total time: {elapsed}s  ({minutes:02d}:{seconds:02d})")