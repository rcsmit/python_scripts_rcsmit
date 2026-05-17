"""
sort_files_by_topic.py

Sorts thousands of files into topic-based subdirectories using Claude AI.
Supports PDF, TXT, RTF, DOC, DOCX, XLS, XLSX, CSV, and image files
(JPG, JPEG, PNG, TIFF, BMP, GIF, WEBP — via OCR).

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
    pip install pdfplumber anthropic tqdm python-docx openpyxl pillow pytesseract striprtf

    For DOC (legacy Word) support:
        Linux/Mac: sudo apt install antiword  /  brew install antiword

    For image OCR:
        Mac:   brew install tesseract
        Linux: sudo apt install tesseract-ocr

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

# INPUT_DIR:  Path = Path(".")          # folder containing files to sort
# OUTPUT_DIR: Path = Path("sorted")     # sorted files land here (created if needed)


# INPUT_DIR:  Path = Path(r"C:\Users\rcxsm\Downloads\pdf_ongesorteerd\pdfs")

INPUT_DIR:  Path = Path(r"C:\Users\rcxsm\Downloads\xls ongesorteerd")
OUTPUT_DIR:  Path = Path(r"C:\Users\rcxsm\Downloads\xls ongesorteerd\sorted")
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
    "Service Quality",
    "Bank accounts",
    "Manuals",
    "Tourism",
    "Maps",
    "Other",
]

# ---------------------------------------------------------------------------
# Supported file extensions
# ---------------------------------------------------------------------------



SUPPORTED_EXTENSIONS: set[str] = {
    ".pdf",
    ".txt", ".rtf", ".csv",".html",".htm"
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
BATCH_POLL_INTERVAL: int   = 30       # seconds between batch status polls
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
    # Pure digits  (e.g. "1234567890")
    if stem.isdigit():
        return True
    # UUID pattern  (with or without hyphens)
    if re.fullmatch(
        r"[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}",
        stem, re.I,
    ):
        return True
    # Mostly non-alpha (less than 40% letters)
    letters = sum(c.isalpha() for c in stem)
    if len(stem) >= 4 and letters / len(stem) < 0.4:
        return True
    # Short and no vowels  (e.g. "xkbf", "z7q3")
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
    """Extract text from the first PAGES_TO_EXTRACT pages via pdfplumber.

    Args:
        file_path: Path to the PDF.
        max_chars: Maximum characters to return.

    Returns:
        Extracted text string.
    """
    with pdfplumber.open(str(file_path)) as pdf:
        chunks = [page.extract_text() or "" for page in pdf.pages[:PAGES_TO_EXTRACT]]
    return "\n".join(chunks).strip()[:max_chars]


def _extract_pdf_pdftotext(file_path: Path, max_chars: int) -> str:
    """Extract text using the native pdftotext binary (faster alternative).

    Requires poppler: brew install poppler / apt install poppler-utils.
    Falls back to pdfplumber if not available.

    Args:
        file_path: Path to the PDF.
        max_chars: Maximum characters to return.

    Returns:
        Extracted text string.
    """
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
    """Read a plain-text or CSV file, trying common encodings.

    Args:
        file_path: Path to the file.
        max_chars: Maximum characters to return.

    Returns:
        File content string.
    """
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return file_path.read_text(encoding=encoding)[:max_chars]
        except UnicodeDecodeError:
            continue
    return ""


def _extract_rtf(file_path: Path, max_chars: int) -> str:
    """Extract plain text from an RTF file using striprtf.

    Args:
        file_path: Path to the RTF file.
        max_chars: Maximum characters to return.

    Returns:
        Plain text content.
    """
    from striprtf.striprtf import rtf_to_text  # type: ignore
    raw = file_path.read_text(encoding="latin-1")
    return rtf_to_text(raw)[:max_chars]


def _extract_docx(file_path: Path, max_chars: int) -> str:
    """Extract paragraph text from a DOCX file via python-docx.

    Args:
        file_path: Path to the DOCX file.
        max_chars: Maximum characters to return.

    Returns:
        Paragraph text joined by newlines.
    """
    import docx  # type: ignore
    doc = docx.Document(str(file_path))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return text[:max_chars]


def _extract_doc(file_path: Path, max_chars: int) -> str:
    """Extract text from a legacy DOC file via antiword.

    Falls back to empty string if antiword is not installed.

    Args:
        file_path: Path to the DOC file.
        max_chars: Maximum characters to return.

    Returns:
        Extracted text string.
    """
    try:
        result = subprocess.run(
            ["antiword", str(file_path)],
            capture_output=True, text=True, timeout=15,
        )
        return result.stdout.strip()[:max_chars]
    except FileNotFoundError:
        log.debug("antiword not found; cannot extract .doc: %s", file_path.name)
        return ""


def _extract_xlsx(file_path: Path, max_chars: int) -> str:
    """Extract cell values from the first 3 sheets (50 rows each) of an XLSX.

    Args:
        file_path: Path to the XLSX/XLS file.
        max_chars: Maximum characters to return.

    Returns:
        Tab/newline separated cell values.
    """
    import openpyxl  # type: ignore
    wb = openpyxl.load_workbook(str(file_path), read_only=True, data_only=True)
    chunks: list[str] = []
    for sheet in wb.worksheets[:3]:
        for row in sheet.iter_rows(max_row=50, values_only=True):
            row_text = "  ".join(str(c) for c in row if c is not None)
            if row_text.strip():
                chunks.append(row_text)
    return "\n".join(chunks)[:max_chars]


def _extract_image(file_path: Path, max_chars: int) -> str:
    """Extract text from an image via Tesseract OCR.

    Requires: pip install pillow pytesseract
    And: brew install tesseract / apt install tesseract-ocr

    Args:
        file_path: Path to the image file.
        max_chars: Maximum characters to return.

    Returns:
        OCR text string, or empty string if tesseract is unavailable.
    """
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


def extract_text_from_file(file_path: Path, max_chars: int) -> str:
    """Dispatch text extraction to the correct handler based on file extension.

    Args:
        file_path: Path to the file.
        max_chars: Maximum characters to return.

    Returns:
        Extracted text string, possibly empty if unreadable or unsupported.
    """
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _extract_pdf(file_path, max_chars)
        elif suffix in (".txt", ".csv",".htm",".html"):
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
    """Fill FileRecord.text for each record in-place using a thread pool.

    Args:
        records:   List of FileRecord objects to populate.
        max_chars: Passed through to extract_text_from_file.
        workers:   Number of parallel threads.
    """
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
    """Build the classification prompt, requesting a suggested name for bad filenames.

    Args:
        batch:  FileRecord objects with text populated.
        topics: Allowed topic label strings.

    Returns:
        Formatted prompt string.
    """
    topic_list = "\n".join(f"- {t}" for t in topics)
    needs_rename = any(_is_bad_filename(r.path.stem) for r in batch)

    entries: list[str] = []
    for i, record in enumerate(batch):
        snippet  = record.text if record.text else "(no text extracted)"
        ext      = record.path.suffix.upper()
        tag      = " [NEEDS_RENAME]" if _is_bad_filename(record.path.stem) else ""
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
        True if parsing succeeded.
    """
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]

    results: list[dict] = json.loads(text.strip())
    for item in results:
        idx: int = int(item["index"])
        topic: str = item["topic"].strip()
        if topic not in topics:
            topic = _best_match(topic, topics)
        batch[idx].topic = topic
        if "suggested_name" in item:
            batch[idx].new_name = _sanitize_suggested_name(str(item["suggested_name"]))
    return True


def _best_match(topic: str, allowed: list[str]) -> str:
    """Return the best-matching allowed topic via case-insensitive substring.

    Args:
        topic:   Returned topic not in the allowed list.
        allowed: Valid topic strings.

    Returns:
        Best matching allowed topic, or 'Other' as fallback.
    """
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
    """Classify a batch via the synchronous Messages API.

    Args:
        client:      Anthropic client instance.
        batch:       FileRecord list to classify in-place.
        topics:      Allowed topic strings.
        retries:     Number of retry attempts on transient failure.
        retry_delay: Seconds to wait between retries.
    """
    prompt = build_classification_prompt(batch, topics)

    for attempt in range(1, retries + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            if _parse_classification_response(response.content[0].text, batch, topics):
                return
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
    """Build Batch API request dicts; assign custom_ids to all records.

    Args:
        all_records: FileRecord objects with text populated.
        topics:      Allowed topic strings.
        batch_size:  Files per sub-batch request.

    Returns:
        List of request dicts for client.beta.messages.batches.create().
    """
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
    """Submit all requests to the Batch API and save state for collect phase.

    Args:
        client:      Anthropic client instance.
        all_records: Records with text extracted.
        topics:      Allowed topic strings.
        batch_size:  Files per sub-batch request.
        state_path:  Path to write the batch state JSON.

    Returns:
        Anthropic batch ID string.
    """
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
    """Block until the batch reaches the 'ended' status.

    Args:
        client:        Anthropic client instance.
        batch_id:      Batch ID to poll.
        poll_interval: Seconds between status checks.
    """
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
    """Retrieve batch results; return path → (topic, new_name) mapping.

    Args:
        client:     Anthropic client instance.
        batch_id:   Batch ID to retrieve.
        topics:     Allowed topic strings.
        id_to_path: custom_id → absolute path string (from state file).
        batch_size: Files per sub-batch (for reconstructing record order).

    Returns:
        Dict mapping absolute path strings to (topic, new_name) tuples.
        new_name is an empty string when no rename was suggested.
    """
    # Reconstruct sub-batch structure
    sub_batches: dict[int, list[tuple[int, str, str]]] = {}
    for custom_id, abs_path in id_to_path.items():
        parts   = custom_id.split("_")
        sub_idx = int(parts[0][3:])
        rec_idx = int(parts[1][3:])
        sub_batches.setdefault(sub_idx, []).append((rec_idx, custom_id, abs_path))

    ordered: dict[int, list[tuple[int, str, str]]] = {
        k: sorted(v, key=lambda x: x[0]) for k, v in sub_batches.items()
    }

    path_to_result: dict[str, tuple[str, str]] = {}
    result_count = 0
    log.info("Streaming batch results for %s…", batch_id)

    for result in client.beta.messages.batches.results(batch_id):
        sub_id  = result.custom_id
        sub_idx = int(sub_id[3:])

        if result.result.type != "succeeded":
            log.warning("Sub-batch %s failed: %s", sub_id, result.result.type)
            for _, _, path in ordered.get(sub_idx, []):
                path_to_result[path] = ("Other", "")
            continue

        raw          = result.result.message.content[0].text
        sub_entries  = ordered.get(sub_idx, [])
        stub_records = [FileRecord(path=Path(p), custom_id=cid) for _, cid, p in sub_entries]

        try:
            _parse_classification_response(raw, stub_records, topics)
            for record in stub_records:
                path_to_result[str(record.path.resolve())] = (record.topic or "Other", record.new_name)
                result_count += 1
        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
            log.warning("Parse error sub-batch %s: %s", sub_id, exc)
            for record in stub_records:
                path_to_result[str(record.path.resolve())] = ("Other", "")

    log.info("Collected results for %d files.", result_count)
    return path_to_result


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def sanitize_folder_name(topic: str) -> str:
    """Convert a topic string to a filesystem-safe directory name.

    Args:
        topic: Raw topic string.

    Returns:
        Safe folder name.
    """
    for ch in r'/\:*?"<>|&':
        topic = topic.replace(ch, "_")
    return topic.strip().strip(".")


def move_or_copy_file(
    record: FileRecord,
    output_dir: Path,
    copy: bool,
    dry_run: bool,
) -> bool:
    """Move or copy a file into its topic subfolder, applying rename if set.

    Args:
        record:     FileRecord with topic and optional new_name.
        output_dir: Root output directory.
        copy:       Copy instead of move.
        dry_run:    Preview only; do not touch files.

    Returns:
        True if the operation succeeded (or would succeed in dry-run).
    """
    folder_name = sanitize_folder_name(record.topic)
    dest_dir    = output_dir / folder_name

    filename = (record.new_name + record.path.suffix) if record.new_name else record.path.name
    dest_path = dest_dir / filename

    # Resolve filename collisions
    if dest_path.exists() and not dry_run:
        stem    = Path(filename).stem
        suffix  = record.path.suffix
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter  += 1

    if dry_run:
        action = "COPY" if copy else "MOVE"
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
    """Move/copy all files based on path→(topic, new_name); update progress.

    Args:
        path_to_result: Mapping of absolute paths to (topic, new_name) tuples.
        output_dir:     Root output directory.
        copy:           Copy instead of move.
        dry_run:        Preview only.
        done:           Existing progress dict, updated in-place.
        progress_path:  Path to persist updated progress.

    Returns:
        SortStats with move counts and per-topic/type breakdown.
    """
    stats       = SortStats()
    stats.total = len(path_to_result)

    for abs_path_str, (topic, new_name) in tqdm(
        path_to_result.items(), desc="Moving files", unit="file"
    ):
        record = FileRecord(path=Path(abs_path_str), topic=topic, new_name=new_name)
        success = move_or_copy_file(record, output_dir, copy=copy, dry_run=dry_run)
        if success:
            stats.moved  += 1
            stats.classified += 1
            if new_name:
                stats.renamed += 1
            stats.topic_counts[topic] = stats.topic_counts.get(topic, 0) + 1
            ext = record.path.suffix.lower()
            stats.type_counts[ext]  = stats.type_counts.get(ext, 0) + 1
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
    """Load previously completed path→topic mappings from disk.

    Args:
        progress_path: Path to the JSON progress file.

    Returns:
        Dict mapping absolute path strings to topic strings.
    """
    if progress_path.exists():
        try:
            with open(progress_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            log.warning("Could not read progress file; starting fresh.")
    return {}


def save_progress(progress_path: Path, done: dict[str, str]) -> None:
    """Persist completed path→topic mappings to disk.

    Args:
        progress_path: Path to write the JSON progress file.
        done:          Dict mapping absolute path strings to topic strings.
    """
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
        SystemExit: If the state file is missing or unreadable.
    """
    if not state_path.exists():
        log.error(
            "Batch state file not found: %s\n"
            "  → Run submit phase first (without --collect).",
            state_path,
        )
        raise SystemExit(1)
    try:
        with open(state_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        log.error("Could not read batch state: %s", exc)
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def collect_files(input_dir: Path) -> list[Path]:
    """Recursively find all supported files under input_dir.

    Args:
        input_dir: Root directory to search.

    Returns:
        Sorted list of absolute file paths with supported extensions.
    """
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
    """Standard pipeline: discover → extract → classify (real-time) → move.

    Args:
        input_dir:  Source directory.
        output_dir: Destination root directory.
        topics:     Allowed topic labels.
        dry_run:    Preview mode.
        copy:       Copy instead of move.
        batch_size: Files per API call.
        workers:    Parallel extraction threads.

    Returns:
        SortStats with final counts.
    """
    stats = SortStats()
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

    log.info("Extracting text using %d threads…", workers)
    extract_texts_parallel(pending, MAX_CHARS_PER_FILE, workers)

    batches = [pending[i: i + batch_size] for i in range(0, len(pending), batch_size)]
    log.info("Classifying %d batches via standard API…", len(batches))
    for batch in tqdm(batches, desc="Classifying", unit="batch"):
        classify_batch_standard(client, batch, topics, API_RETRY_ATTEMPTS, API_RETRY_DELAY)
        stats.classified += sum(1 for r in batch if r.topic and r.error != "classification_failed")
        stats.failed     += sum(1 for r in batch if r.error == "classification_failed")

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
) -> str:
    """Batch phase 1: extract text and submit to Batch API.

    Args:
        input_dir:  Source directory.
        output_dir: Output/state directory.
        topics:     Allowed topic labels.
        batch_size: Files per sub-batch request.
        workers:    Parallel extraction threads.

    Returns:
        Anthropic batch ID, or empty string if nothing to submit.
    """
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

    log.info("Extracting text using %d threads…", workers)
    extract_texts_parallel(pending, MAX_CHARS_PER_FILE, workers)

    batch_id = submit_batch(client, pending, topics, batch_size, state_path)
    log.info(
        "\nBatch submitted! Wait for it to finish (minutes to ~1 hour), then run:\n"
        "  python sort_files_by_topic.py --collect",
    )
    return batch_id


def run_batch_collect_phase(output_dir: Path, copy: bool, dry_run: bool, wait: bool) -> SortStats:
    """Batch phase 2: retrieve results and move files.

    Args:
        output_dir: Directory containing state and progress files.
        copy:       Copy instead of move.
        dry_run:    Preview only.
        wait:       Poll until batch finishes before collecting.

    Returns:
        SortStats with move counts, or empty SortStats if batch not yet done.
    """
    client     = _get_client()
    state_path = output_dir / BATCH_STATE_FILE
    state      = load_batch_state(state_path)

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

    stats = apply_topics_and_move(
        path_to_result=path_to_result,
        output_dir=output_dir,
        copy=copy,
        dry_run=dry_run,
        done=done,
        progress_path=progress_path,
    )

    if not dry_run and state_path.exists():
        state_path.unlink()
        log.info("Batch state file removed.")

    return stats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client() -> anthropic.Anthropic:
    """Create and return an Anthropic client, raising clearly if key is missing.

    Returns:
        Configured Anthropic client.

    Raises:
        EnvironmentError: If ANTHROPIC_API_KEY is not set.
    """
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
    """Print a human-readable summary of the sorting run.

    Args:
        stats:   Populated SortStats instance.
        dry_run: Whether this was a preview run.
        mode:    Mode label (e.g. 'standard', 'batch-collect').
    """
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
    """Parse command-line arguments.

    Returns:
        Parsed argparse Namespace.
    """
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
    parser.add_argument(
        "--input", "-i", type=Path, default=None,
        help=f"Input directory (default: INPUT_DIR = '{INPUT_DIR}').",
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help=f"Output directory (default: OUTPUT_DIR = '{OUTPUT_DIR}').",
    )
    parser.add_argument(
        "--topics", "-t", default=None,
        help="Comma-separated topic labels. Defaults to built-in list.",
    )
    parser.add_argument(
        "--standard", action="store_true",
        help="Use real-time standard API instead of batch.",
    )
    parser.add_argument(
        "--collect", action="store_true",
        help="Collect batch results and move files (run after submit).",
    )
    parser.add_argument(
        "--wait", action="store_true",
        help="Submit (if needed) then block until done and collect automatically.",
    )
    parser.add_argument(
        "--batch-size", type=int, default=BATCH_SIZE,
        help=f"Files per API request (default: {BATCH_SIZE}).",
    )
    parser.add_argument(
        "--workers", type=int, default=MAX_WORKERS,
        help=f"Parallel extraction threads (default: {MAX_WORKERS}).",
    )
    parser.add_argument(
        "--copy", action="store_true",
        help="Copy files instead of moving them.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview without touching any files.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point: parse args, validate, dispatch to correct pipeline."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve directories: CLI overrides > module-level constants
    input_dir  = args.input  if args.input  else INPUT_DIR
    output_dir = args.output if args.output else OUTPUT_DIR

    input_dir  = input_dir.resolve()
    output_dir = output_dir.resolve()

    if not input_dir.is_dir():
        log.error("Input directory does not exist: %s", input_dir)
        raise SystemExit(1)

    # Create output dir early so state files have a home
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

    # ---- Dispatch ----

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
        # Default: submit + wait + collect — all in one run, no flags needed
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