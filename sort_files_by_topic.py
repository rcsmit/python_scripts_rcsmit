#!/usr/bin/env python3
"""
sort_pdfs_by_topic.py

Sorts thousands of files into topic-based subdirectories using Claude AI.
Supports PDF, TXT, RTF, DOC, DOCX, XLS, XLSX, CSV, and image files
(JPG, JPEG, PNG, TIFF, BMP, GIF, WEBP — via OCR).

Supports two modes:

  STANDARD mode  — real-time API calls, results arrive immediately.
  BATCH mode     — submits all requests to the Anthropic Batch API (50% cheaper),
                   polls until complete, then moves files. Recommended for large runs.

Two-phase workflow for batch mode:
  Phase 1 (submit):  python sort_pdfs_by_topic.py --input /pdfs --output /sorted --batch
  Phase 2 (collect): python sort_pdfs_by_topic.py --input /pdfs --output /sorted --batch --collect

Or run both phases automatically (script polls until done):
  python sort_pdfs_by_topic.py --input pdfs --output sorted --batch --wait

Usage examples:
    # Standard (immediate, higher cost)
    python sort_pdfs_by_topic.py --input /pdfs --output /sorted

    # Batch (50% cheaper, async — submit then collect later)
    python sort_pdfs_by_topic.py --input /pdfs --output /sorted --batch
    python sort_pdfs_by_topic.py --input /pdfs --output /sorted --batch --collect

    # Batch with auto-wait (blocks until batch finishes, then moves files)
    python sort_pdfs_by_topic.py --input /pdfs --output /sorted --batch --wait

    # Dry-run preview
    python sort_pdfs_by_topic.py --input /pdfs --output /sorted --dry-run

    # Custom topics, copy instead of move
    python sort_pdfs_by_topic.py --input /pdfs --output /sorted \\
        --topics "Finance,Legal,Medical,Technical" --copy

Requirements:
    pip install pdfplumber anthropic tqdm python-docx openpyxl pillow pytesseract striprtf

    For DOC (old Word format) support on Linux:
        sudo apt install antiword

    For image OCR support:
        Mac:   brew install tesseract
        Linux: sudo apt install tesseract-ocr

Environment:
    ANTHROPIC_API_KEY must be set.

How to set the API key:

    1. Create an account
    Go to console.anthropic.com and sign in or create an account — you can use email or Google.

    2. Add a payment method
    Add a payment method under Billing — the API is pay-as-you-go, no subscription required.
    New accounts get ~$5 in free trial credits, so you can test before spending anything.

    3. Generate the key
    Navigate to API Keys and click Create Key. Name it (e.g. "pdf-sorter") and copy it
    immediately — it won't be shown again after you close the dialog.

    4. Set it in your terminal
    On Mac/Linux:
        export ANTHROPIC_API_KEY="sk-ant-..."
    On Windows (Command Prompt):
        set ANTHROPIC_API_KEY=sk-ant-...
    On Windows (PowerShell):
        $env:ANTHROPIC_API_KEY="sk-ant-..."

    To make it permanent, add the export line to your ~/.bashrc or ~/.zshrc file.

    Note: The key starts with sk-ant-. Never put it directly in your Python script
    or commit it to Git — always use the environment variable as the script does.

    For 10,000 files at ~$7, add €10–15 in credits to start.

Costs:
    17/05/2026 : EUR 0.27 for 433 pdfs
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

import anthropic
import pdfplumber
from tqdm import tqdm

# Suppress noisy library loggers before basicConfig
logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pypdf").setLevel(logging.ERROR)
logging.getLogger("pypdf._reader").setLevel(logging.ERROR)
logging.getLogger("pypdf._page").setLevel(logging.ERROR)
logging.getLogger("pypdf.generic").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# Configuration
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

# Supported file extensions and their type groups
SUPPORTED_EXTENSIONS: set[str] = {
    # Documents
    ".pdf",
    ".txt", ".rtf",
    ".doc", ".docx",
    ".xls", ".xlsx",
    ".csv",
    # Images (OCR)
    ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif", ".webp",
}

# Model to use — Haiku is cheapest and sufficient for classification
MODEL: str = "claude-haiku-4-5-20251001"

PAGES_TO_EXTRACT: int = 2         # Number of pages to read per PDF/DOCX
MAX_CHARS_PER_FILE: int = 3_000   # Truncate extracted text to this length
BATCH_SIZE: int = 10              # Files per API request (standard and batch)
MAX_WORKERS: int = 16             # Parallel text-extraction threads
API_RETRY_ATTEMPTS: int = 3       # Retries on transient API errors (standard mode)
API_RETRY_DELAY: float = 5.0      # Seconds between retries
BATCH_POLL_INTERVAL: int = 30     # Seconds between batch status polls
PROGRESS_FILE: str = "sort_progress.json"
BATCH_STATE_FILE: str = "sort_batch_state.json"

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
    """Holds metadata and extracted text for a single file.

    Attributes:
        path: Absolute path to the file.
        text: Extracted text snippet.
        topic: Assigned topic after classification.
        error: Error message if extraction or classification failed.
        custom_id: Unique ID used to correlate batch requests with records.
    """
    path: Path
    text: str = ""
    topic: str = ""
    error: str = ""
    custom_id: str = ""


@dataclass
class SortStats:
    """Running statistics for the sorting run.

    Attributes:
        total: Total files found.
        classified: Successfully classified.
        moved: Successfully moved/copied.
        skipped: Already processed (resume).
        failed: Extraction or API failures.
        topic_counts: Counter per topic.
        type_counts: Counter per file extension.
    """
    total: int = 0
    classified: int = 0
    moved: int = 0
    skipped: int = 0
    failed: int = 0
    topic_counts: dict[str, int] = field(default_factory=dict)
    type_counts: dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Text extraction — per file type
# ---------------------------------------------------------------------------

def _extract_pdf(file_path: Path, max_chars: int) -> str:
    """Extract text from the first PAGES_TO_EXTRACT pages of a PDF using pdfplumber.

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
    """Extract text using the native pdftotext binary (faster alternative to pdfplumber).

    Requires poppler-utils: brew install poppler / apt install poppler-utils

    Args:
        file_path: Path to the PDF.
        max_chars: Maximum characters to return.

    Returns:
        Extracted text string, or empty string if pdftotext is unavailable.
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
    """Extract text from a plain-text or CSV file, trying common encodings.

    Args:
        file_path: Path to the text file.
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
    from striprtf.striprtf import rtf_to_text
    raw = file_path.read_text(encoding="latin-1")
    return rtf_to_text(raw)[:max_chars]


def _extract_docx(file_path: Path, max_chars: int) -> str:
    """Extract text from a DOCX file using python-docx.

    Args:
        file_path: Path to the DOCX file.
        max_chars: Maximum characters to return.

    Returns:
        Paragraph text joined by newlines.
    """
    import docx
    doc = docx.Document(str(file_path))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return text[:max_chars]


def _extract_doc(file_path: Path, max_chars: int) -> str:
    """Extract text from a legacy DOC file using antiword (Linux/Mac).

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
        log.debug("antiword not found; cannot extract .doc file %s", file_path.name)
        return ""


def _extract_xlsx(file_path: Path, max_chars: int) -> str:
    """Extract text from the first 3 sheets of an XLSX file (first 50 rows each).

    Args:
        file_path: Path to the XLSX file.
        max_chars: Maximum characters to return.

    Returns:
        Tab/newline separated cell values.
    """
    import openpyxl
    wb = openpyxl.load_workbook(str(file_path), read_only=True, data_only=True)
    chunks: list[str] = []
    for sheet in wb.worksheets[:3]:
        for row in sheet.iter_rows(max_row=50, values_only=True):
            row_text = "  ".join(str(c) for c in row if c is not None)
            if row_text.strip():
                chunks.append(row_text)
    return "\n".join(chunks)[:max_chars]


def _extract_image(file_path: Path, max_chars: int) -> str:
    """Extract text from an image file using Tesseract OCR via pytesseract.

    Requires: pip install pillow pytesseract
    And: brew install tesseract / apt install tesseract-ocr

    Args:
        file_path: Path to the image file.
        max_chars: Maximum characters to return.

    Returns:
        OCR text string, or empty string if tesseract is unavailable.
    """
    try:
        import pytesseract
        from PIL import Image
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
        file_path: Path to the file to extract text from.
        max_chars: Maximum characters to return.

    Returns:
        Extracted text string, possibly empty if the file is unreadable
        or the type is unsupported.
    """
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _extract_pdf(file_path, max_chars)
        elif suffix in (".txt", ".csv"):
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
        else:
            return ""
    except Exception as exc:
        log.debug("Extraction failed for %s: %s", file_path.name, exc)
        return ""


# ---------------------------------------------------------------------------
# Parallel extraction
# ---------------------------------------------------------------------------

def extract_texts_parallel(
    records: list[FileRecord],
    max_chars: int,
    workers: int,
) -> None:
    """Fill FileRecord.text for each record in-place using a thread pool.

    Args:
        records: List of FileRecord objects to populate.
        max_chars: Passed through to extract_text_from_file.
        workers: Number of parallel threads.
    """
    def _extract(record: FileRecord) -> None:
        record.text = extract_text_from_file(record.path, max_chars)
        if not record.text:
            record.error = "empty_text"

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_extract, r): r for r in records}
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Extracting text",
            unit="file",
        ):
            future.result()


# ---------------------------------------------------------------------------
# Prompt builder (shared by both modes)
# ---------------------------------------------------------------------------

def build_classification_prompt(batch: list[FileRecord], topics: list[str]) -> str:
    """Build the user prompt for topic classification.

    Args:
        batch: FileRecord objects with text populated.
        topics: Allowed topic label strings.

    Returns:
        Formatted prompt string.
    """
    topic_list = "\n".join(f"- {t}" for t in topics)
    entries: list[str] = []
    for i, record in enumerate(batch):
        snippet = record.text if record.text else "(no text extracted)"
        ext = record.path.suffix.upper()
        entries.append(f"### File {i} [{ext}]\nFilename: {record.path.name}\n\n{snippet}")
    docs_block = "\n\n".join(entries)

    return (
        "You are a document classifier. Assign exactly one topic from the list below to each file.\n\n"
        f"Allowed topics:\n{topic_list}\n\n"
        "Return ONLY a JSON array with one object per file, in the same order as provided.\n"
        "Each object must have exactly two keys: \"index\" (integer) and \"topic\" (string from the list above).\n"
        "Do not include any explanation or markdown — only raw JSON.\n\n"
        f"Files to classify:\n\n{docs_block}\n"
    )


def _parse_classification_response(raw: str, batch: list[FileRecord], topics: list[str]) -> bool:
    """Parse a classification JSON response and populate batch records in-place.

    Args:
        raw: Raw text response from Claude.
        batch: Records to populate with topics.
        topics: Allowed topic strings for validation.

    Returns:
        True if parsing succeeded, False otherwise.
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
    return True


def _best_match(topic: str, allowed: list[str]) -> str:
    """Return the best-matching allowed topic via case-insensitive substring.

    Args:
        topic: Returned topic string not in the allowed list.
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
    """Classify a batch via the standard (synchronous) Messages API.

    Args:
        client: Anthropic client instance.
        batch: FileRecord list to classify in-place.
        topics: Allowed topic strings.
        retries: Number of retry attempts on transient failure.
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
            raw = response.content[0].text
            if _parse_classification_response(raw, batch, topics):
                return
        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
            log.warning("Parse error on attempt %d/%d: %s", attempt, retries, exc)
        except anthropic.RateLimitError:
            wait = retry_delay * 2
            log.warning("Rate limited; waiting %.0fs (attempt %d/%d)", wait, attempt, retries)
            time.sleep(wait)
        except anthropic.APIStatusError as exc:
            log.warning("API error %s on attempt %d/%d", exc.status_code, attempt, retries)
            time.sleep(retry_delay)

        if attempt < retries:
            time.sleep(retry_delay)

    for record in batch:
        if not record.topic:
            record.error = "classification_failed"
            record.topic = "Other"


# ---------------------------------------------------------------------------
# Batch API — submit phase
# ---------------------------------------------------------------------------

def build_batch_requests(
    all_records: list[FileRecord],
    topics: list[str],
    batch_size: int,
) -> list[dict]:
    """Build the list of MessageBatchRequestParam dicts for the Batch API.

    Each request classifies up to `batch_size` files. The custom_id encodes
    the sub-batch index so results can be matched back to records.

    Args:
        all_records: All pending FileRecord objects with text populated.
        topics: Allowed topic strings.
        batch_size: Files per individual request inside the batch.

    Returns:
        List of request param dicts for client.beta.messages.batches.create().
    """
    requests: list[dict] = []
    sub_batches = [
        all_records[i : i + batch_size]
        for i in range(0, len(all_records), batch_size)
    ]
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
    """Submit all classification requests to the Anthropic Batch API.

    Saves the batch_id and a custom_id → file path mapping to disk so the
    collect phase can work without re-extracting text.

    Args:
        client: Anthropic client instance.
        all_records: Records with text already extracted.
        topics: Allowed topic strings.
        batch_size: Files per sub-batch request.
        state_path: Path to write the batch state JSON file.

    Returns:
        The Anthropic batch ID string.
    """
    log.info("Building batch requests…")
    requests = build_batch_requests(all_records, topics, batch_size)
    log.info("Submitting %d requests to Batch API…", len(requests))

    response = client.beta.messages.batches.create(requests=requests)
    batch_id: str = response.id
    log.info("Batch submitted. ID: %s  |  Status: %s", batch_id, response.processing_status)

    id_to_path: dict[str, str] = {
        record.custom_id: str(record.path.resolve())
        for record in all_records
    }
    state = {
        "batch_id": batch_id,
        "topics": topics,
        "batch_size": batch_size,
        "id_to_path": id_to_path,
    }
    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
    log.info("Batch state saved to %s", state_path)

    return batch_id


# ---------------------------------------------------------------------------
# Batch API — collect phase
# ---------------------------------------------------------------------------

def poll_batch_until_done(
    client: anthropic.Anthropic,
    batch_id: str,
    poll_interval: int,
) -> None:
    """Block until the batch reaches the 'ended' status.

    Args:
        client: Anthropic client instance.
        batch_id: The Anthropic batch ID to poll.
        poll_interval: Seconds between status checks.
    """
    log.info("Polling batch %s every %ds…", batch_id, poll_interval)
    while True:
        batch = client.beta.messages.batches.retrieve(batch_id)
        status = batch.processing_status
        counts = batch.request_counts
        log.info(
            "Status: %-12s  processing=%d  succeeded=%d  errored=%d",
            status,
            counts.processing,
            counts.succeeded,
            counts.errored,
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
) -> dict[str, str]:
    """Retrieve batch results and return a path → topic mapping.

    Args:
        client: Anthropic client instance.
        batch_id: Batch ID to retrieve results for.
        topics: Allowed topic strings for validation.
        id_to_path: Mapping of custom_id → absolute path string.
        batch_size: Files per sub-batch (used to reconstruct record order).

    Returns:
        Dict mapping absolute path strings to assigned topic strings.
    """
    sub_batches: dict[int, list[tuple[int, str, str]]] = {}
    for custom_id, abs_path in id_to_path.items():
        parts = custom_id.split("_")
        sub_idx = int(parts[0][3:])
        rec_idx = int(parts[1][3:])
        sub_batches.setdefault(sub_idx, []).append((rec_idx, custom_id, abs_path))

    ordered_sub_batches: dict[int, list[tuple[int, str, str]]] = {
        k: sorted(v, key=lambda x: x[0]) for k, v in sub_batches.items()
    }

    path_to_topic: dict[str, str] = {}
    result_count = 0
    log.info("Streaming batch results for %s…", batch_id)

    for result in client.beta.messages.batches.results(batch_id):
        sub_id: str = result.custom_id
        sub_idx = int(sub_id[3:])

        if result.result.type != "succeeded":
            log.warning("Sub-batch %s failed with type: %s", sub_id, result.result.type)
            for _, _, path in ordered_sub_batches.get(sub_idx, []):
                path_to_topic[path] = "Other"
            continue

        raw: str = result.result.message.content[0].text
        sub_entries = ordered_sub_batches.get(sub_idx, [])
        stub_records: list[FileRecord] = [
            FileRecord(path=Path(path), custom_id=cid)
            for _, cid, path in sub_entries
        ]

        try:
            _parse_classification_response(raw, stub_records, topics)
            for record in stub_records:
                path_to_topic[str(record.path.resolve())] = record.topic or "Other"
                result_count += 1
        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
            log.warning("Parse error for sub-batch %s: %s", sub_id, exc)
            for record in stub_records:
                path_to_topic[str(record.path.resolve())] = "Other"

    log.info("Collected topics for %d files.", result_count)
    return path_to_topic


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def sanitize_folder_name(topic: str) -> str:
    """Convert a topic string to a safe directory name.

    Args:
        topic: Raw topic string.

    Returns:
        Filesystem-safe folder name.
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
    """Move or copy a file into the appropriate topic subfolder.

    Args:
        record: FileRecord with topic assigned.
        output_dir: Root output directory.
        copy: If True, copy instead of move.
        dry_run: If True, log action but do not touch files.

    Returns:
        True if the operation succeeded (or would succeed in dry-run).
    """
    folder_name = sanitize_folder_name(record.topic)
    dest_dir = output_dir / folder_name
    dest_path = dest_dir / record.path.name

    if dest_path.exists() and not dry_run:
        stem = record.path.stem
        suffix = record.path.suffix
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1

    if dry_run:
        log.debug(
            "%s [DRY-RUN] %s -> %s/",
            "COPY" if copy else "MOVE",
            record.path.name,
            folder_name,
        )
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
    path_to_topic: dict[str, str],
    output_dir: Path,
    copy: bool,
    dry_run: bool,
    done: dict[str, str],
    progress_path: Path,
) -> SortStats:
    """Move/copy files based on a path→topic dict; update progress checkpoint.

    Args:
        path_to_topic: Mapping of absolute path strings to topic strings.
        output_dir: Root output directory for topic subfolders.
        copy: Copy instead of move.
        dry_run: Preview only.
        done: Existing progress dict, updated in-place.
        progress_path: Path to persist updated progress.

    Returns:
        SortStats with move counts and per-topic breakdown.
    """
    stats = SortStats()
    stats.total = len(path_to_topic)

    for abs_path_str, topic in tqdm(path_to_topic.items(), desc="Moving files", unit="file"):
        record = FileRecord(path=Path(abs_path_str), topic=topic)
        success = move_or_copy_file(record, output_dir, copy=copy, dry_run=dry_run)
        if success:
            stats.moved += 1
            stats.classified += 1
            stats.topic_counts[topic] = stats.topic_counts.get(topic, 0) + 1
            ext = record.path.suffix.lower()
            stats.type_counts[ext] = stats.type_counts.get(ext, 0) + 1
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
# Progress / resume helpers
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
        done: Dict mapping absolute path strings to topic strings.
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
            "  → Run the submit phase first (without --collect).",
            state_path,
        )
        raise SystemExit(1)
    try:
        with open(state_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        log.error("Could not read batch state file: %s", exc)
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
# Top-level pipelines
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
        input_dir: Source directory containing files.
        output_dir: Destination root directory.
        topics: Allowed topic labels.
        dry_run: Preview mode; no files are touched.
        copy: Copy files instead of moving them.
        batch_size: Files per API call.
        workers: Parallel text-extraction threads.

    Returns:
        SortStats with final counts.
    """
    stats = SortStats()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")
    client = anthropic.Anthropic(api_key=api_key)

    progress_path = output_dir / PROGRESS_FILE
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    done: dict[str, str] = {} if dry_run else load_progress(progress_path)

    all_files = collect_files(input_dir)
    stats.total = len(all_files)
    log.info("Found %d supported files in %s", stats.total, input_dir)

    pending: list[FileRecord] = []
    for file_path in all_files:
        key = str(file_path.resolve())
        if key in done:
            stats.skipped += 1
        else:
            pending.append(FileRecord(path=file_path))

    log.info("%d pending  |  %d skipped (already done)", len(pending), stats.skipped)
    if not pending:
        log.info("Nothing to do.")
        return stats

    log.info("Extracting text using %d threads…", workers)
    extract_texts_parallel(pending, MAX_CHARS_PER_FILE, workers)

    batches = [pending[i : i + batch_size] for i in range(0, len(pending), batch_size)]
    log.info("Classifying %d batches via standard API…", len(batches))
    for batch in tqdm(batches, desc="Classifying", unit="batch"):
        classify_batch_standard(client, batch, topics, API_RETRY_ATTEMPTS, API_RETRY_DELAY)
        stats.classified += sum(1 for r in batch if r.topic and r.error != "classification_failed")
        stats.failed += sum(1 for r in batch if r.error == "classification_failed")

    log.info("Moving files%s…", " [DRY-RUN]" if dry_run else "")
    for record in tqdm(pending, desc="Moving files", unit="file"):
        if not record.topic:
            stats.failed += 1
            continue
        success = move_or_copy_file(record, output_dir, copy=copy, dry_run=dry_run)
        if success:
            stats.moved += 1
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
    """Batch pipeline phase 1: extract text and submit to Batch API.

    Args:
        input_dir: Source directory containing files.
        output_dir: Used to locate progress and state files.
        topics: Allowed topic labels.
        batch_size: Files per sub-batch request.
        workers: Parallel text-extraction threads.

    Returns:
        The Anthropic batch ID string, or empty string if nothing to submit.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")
    client = anthropic.Anthropic(api_key=api_key)

    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = output_dir / PROGRESS_FILE
    state_path = output_dir / BATCH_STATE_FILE
    done = load_progress(progress_path)

    all_files = collect_files(input_dir)
    log.info("Found %d supported files.", len(all_files))

    pending: list[FileRecord] = []
    skipped = 0
    for file_path in all_files:
        key = str(file_path.resolve())
        if key in done:
            skipped += 1
        else:
            pending.append(FileRecord(path=file_path))

    log.info("%d pending  |  %d skipped (already done)", len(pending), skipped)
    if not pending:
        log.info("Nothing to submit.")
        return ""

    log.info("Extracting text using %d threads…", workers)
    extract_texts_parallel(pending, MAX_CHARS_PER_FILE, workers)

    batch_id = submit_batch(client, pending, topics, batch_size, state_path)
    log.info(
        "\nBatch submitted! Wait for it to finish (usually minutes to an hour), then run:\n"
        "  python sort_pdfs_by_topic.py --input %s --output %s --batch --collect",
        input_dir,
        output_dir,
    )
    return batch_id


def run_batch_collect_phase(
    output_dir: Path,
    copy: bool,
    dry_run: bool,
    wait: bool,
) -> SortStats:
    """Batch pipeline phase 2: retrieve results and move files.

    Args:
        output_dir: Directory containing the batch state and progress files.
        copy: Copy files instead of moving them.
        dry_run: Preview mode; no files are touched.
        wait: If True, poll until the batch finishes before collecting.

    Returns:
        SortStats with move counts, or empty SortStats if batch not yet done.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")
    client = anthropic.Anthropic(api_key=api_key)

    state_path = output_dir / BATCH_STATE_FILE
    state = load_batch_state(state_path)

    batch_id: str = state["batch_id"]
    topics: list[str] = state["topics"]
    batch_size: int = state["batch_size"]
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

    path_to_topic = collect_batch_results(client, batch_id, topics, id_to_path, batch_size)

    progress_path = output_dir / PROGRESS_FILE
    done = load_progress(progress_path)

    stats = apply_topics_and_move(
        path_to_topic=path_to_topic,
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
# Summary printer
# ---------------------------------------------------------------------------

def print_summary(stats: SortStats, dry_run: bool, mode: str) -> None:
    """Print a human-readable summary of the sorting run.

    Args:
        stats: Populated SortStats instance.
        dry_run: Whether this was a preview run.
        mode: Mode label for display (e.g. 'standard', 'batch-collect').
    """
    tag = " [DRY-RUN]" if dry_run else ""
    print(f"\n{'='*54}")
    print(f"  File Sorting Summary  [{mode.upper()}]{tag}")
    print(f"{'='*54}")
    print(f"  Total files found    :  {stats.total:>6}")
    print(f"  Skipped (done)       :  {stats.skipped:>6}")
    print(f"  Classified           :  {stats.classified:>6}")
    print(f"  Moved/Copied         :  {stats.moved:>6}")
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
            "Sort files into topic folders using Claude AI (standard or batch mode).\n"
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        type=Path,
        help="Directory containing files (searched recursively).",
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        type=Path,
        help="Root output directory where topic subfolders will be created.",
    )
    parser.add_argument(
        "--topics", "-t",
        default=None,
        help=(
            "Comma-separated list of topic labels. "
            f"Defaults to built-in list of {len(DEFAULT_TOPICS)} topics."
        ),
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Use the Anthropic Batch API (50%% cheaper, async). Default: standard mode.",
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="[Batch mode] Collect results and move files. Run after the submit phase.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="[Batch mode] Submit (if needed) then block until done and collect automatically.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Files per API request (default: {BATCH_SIZE}).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Parallel text-extraction threads (default: {MAX_WORKERS}).",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of moving them (originals are preserved).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without touching any files.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point: parse args, validate inputs, dispatch to correct pipeline."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.input.is_dir():
        log.error("Input path does not exist or is not a directory: %s", args.input)
        raise SystemExit(1)

    topics: list[str] = (
        [t.strip() for t in args.topics.split(",") if t.strip()]
        if args.topics
        else DEFAULT_TOPICS
    )

    if args.dry_run:
        log.info("DRY-RUN mode — no files will be moved or copied.")

    log.info("Model  : %s", MODEL)
    log.info("Topics (%d): %s", len(topics), ", ".join(topics))
    log.info("Supported extensions: %s", ", ".join(sorted(SUPPORTED_EXTENSIONS)))

    # ---- Dispatch ----

    if args.batch and args.collect:
        stats = run_batch_collect_phase(
            output_dir=args.output,
            copy=args.copy,
            dry_run=args.dry_run,
            wait=False,
        )
        print_summary(stats, dry_run=args.dry_run, mode="batch-collect")

    elif args.batch and args.wait:
        state_path = args.output / BATCH_STATE_FILE
        if not state_path.exists():
            run_batch_submit_phase(
                input_dir=args.input,
                output_dir=args.output,
                topics=topics,
                batch_size=args.batch_size,
                workers=args.workers,
            )
        stats = run_batch_collect_phase(
            output_dir=args.output,
            copy=args.copy,
            dry_run=args.dry_run,
            wait=True,
        )
        print_summary(stats, dry_run=args.dry_run, mode="batch-wait")

    elif args.batch:
        run_batch_submit_phase(
            input_dir=args.input,
            output_dir=args.output,
            topics=topics,
            batch_size=args.batch_size,
            workers=args.workers,
        )

    else:
        stats = run_standard_pipeline(
            input_dir=args.input,
            output_dir=args.output,
            topics=topics,
            dry_run=args.dry_run,
            copy=args.copy,
            batch_size=args.batch_size,
            workers=args.workers,
        )
        print_summary(stats, dry_run=args.dry_run, mode="standard")


if __name__ == "__main__":
    print(f"Start : {time.strftime('%H:%M:%S')}")
    start_time = int(time.time())

    main()

    end_time = int(time.time())
    elapsed = end_time - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"\nEnd   : {time.strftime('%H:%M:%S')}")
    print(f"Total time: {elapsed}s ({minutes:02d}:{seconds:02d})")
