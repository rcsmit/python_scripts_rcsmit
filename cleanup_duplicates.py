"""
cleanup_duplicates.py

Scans two directories recursively and moves files from `old_dir` to a trash
folder if the same file (matching name AND size) exists anywhere in `sorted_dir`.
Empty folders left behind in old_dir are removed afterwards.

Usage:
    python cleanup_duplicates.py [--dry-run]

    --dry-run   Preview what would be moved without actually doing anything.
"""

import shutil
import argparse
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# ── Configuration ────────────────────────────────────────────────────────────
SORTED_DIR = Path(r"C:\\Users\\rcxsm\\Documents")
# OLD_DIR    = Path(r"E:\\Documents")
# TRASH_DIR  = Path(r"E:\\Duplicates")
OLD_DIR = Path(r"C:\\Users\\rcxsm\\Downloads\\UNSORTED")
TRASH_DIR  = Path(r"C:\\Users\\rcxsm\Downloads\\Duplicates")
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def collect_files(root: Path, label: str) -> list[Path]:
    """Collect all files under root, with a spinner while scanning."""
    log.info(f"Collecting files in {label}: {root} ...")
    files = []
    if HAS_TQDM:
        with tqdm(desc=f"  Scanning {label}", unit=" files", dynamic_ncols=True) as bar:
            for path in root.rglob("*"):
                if path.is_file():
                    files.append(path)
                    bar.update(1)
    else:
        for path in root.rglob("*"):
            if path.is_file():
                files.append(path)
        log.info(f"  Found {len(files):,} files.")
    return files


def build_index(files: list[Path], label: str) -> dict[tuple[str, int], list[Path]]:
    """Build (name, size) -> [paths] index with a progress bar."""
    index: dict[tuple[str, int], list[Path]] = defaultdict(list)
    log.info(f"Indexing {label} ({len(files):,} files) ...")
    iterator = (
        tqdm(files, desc=f"  Indexing {label}", unit=" files", dynamic_ncols=True)
        if HAS_TQDM else files
    )
    for path in iterator:
        try:
            key = (path.name, path.stat().st_size)
            index[key].append(path)
        except OSError as e:
            log.warning(f"  Could not stat {path}: {e}")
    log.info(f"  {len(index):,} unique (name, size) combinations.")
    return index


def move_to_trash(file_path: Path, trash_root: Path, dry_run: bool) -> None:
    """Move file_path into trash_root, preserving relative directory structure."""
    try:
        rel = file_path.relative_to(OLD_DIR)
    except ValueError:
        rel = Path(file_path.name)

    dest = trash_root / rel

    # Avoid overwriting an existing file in trash by appending a timestamp
    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        dest = dest.with_name(f"{dest.stem}__{ts}{dest.suffix}")

    if dry_run:
        log.info(f"[DRY-RUN] Would move: {file_path}  ->  {dest}")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(file_path), str(dest))
    log.info(f"Moved: {file_path}  ->  {dest}")


def remove_empty_dirs(root: Path, dry_run: bool) -> None:
    """Remove empty directories under root, deepest first."""
    log.info("Removing empty folders in old dir ...")
    # Sort deepest paths first so children are removed before parents
    all_dirs = sorted(
        [p for p in root.rglob("*") if p.is_dir()],
        key=lambda p: len(p.parts),
        reverse=True,
    )
    removed = 0
    for d in all_dirs:
        if dry_run:
            # Check if it would be empty (no files inside)
            if not any(d.rglob("*")):
                log.info(f"[DRY-RUN] Would remove empty folder: {d}")
                removed += 1
        else:
            try:
                d.rmdir()  # only succeeds if truly empty
                log.info(f"Removed empty folder: {d}")
                removed += 1
            except OSError:
                pass  # not empty — skip
    log.info(f"  {'Would remove' if dry_run else 'Removed'} {removed:,} empty folder(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Move duplicate files from old_dir to trash.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without moving files.")
    args = parser.parse_args()
    dry_run: bool = args.dry_run

    if not HAS_TQDM:
        log.warning("tqdm not installed — no progress bars. Run: pip install tqdm")

    if dry_run:
        log.info("=== DRY-RUN MODE — no files will be moved ===")

    # Validate directories
    for label, path in [("sorted", SORTED_DIR), ("old", OLD_DIR)]:
        if not path.exists():
            log.error(f"{label} directory not found: {path}")
            return

    if not dry_run:
        TRASH_DIR.mkdir(parents=True, exist_ok=True)
        log.info(f"Trash folder: {TRASH_DIR}")

    # Phase 1: collect & index sorted dir
    sorted_files = collect_files(SORTED_DIR, "sorted")
    sorted_index = build_index(sorted_files, "sorted")

    # Phase 2: collect old dir files
    old_files = collect_files(OLD_DIR, "old")
    log.info(f"Checking {len(old_files):,} files in old dir for duplicates ...")

    # Phase 3: match & move
    moved = 0
    skipped = 0
    errors = 0

    iterator = (
        tqdm(
            old_files,
            desc="  Checking / moving",
            unit=" files",
            dynamic_ncols=True,
            postfix={"moved": 0, "kept": 0},
        )
        if HAS_TQDM else old_files
    )

    for old_file in iterator:
        try:
            key = (old_file.name, old_file.stat().st_size)
        except OSError as e:
            log.warning(f"  Could not stat {old_file}: {e}")
            errors += 1
            continue

        if key in sorted_index:
            try:
                move_to_trash(old_file, TRASH_DIR, dry_run)
                moved += 1
            except OSError as e:
                log.error(f"  Failed to move {old_file}: {e}")
                errors += 1
        else:
            skipped += 1

        if HAS_TQDM:
            iterator.set_postfix({"moved": moved, "kept": skipped})

    # Phase 4: remove empty directories
    if moved > 0:
        remove_empty_dirs(OLD_DIR, dry_run)

    # Summary
    log.info("-" * 60)
    log.info(f"{'Would move' if dry_run else 'Moved'}: {moved:,} file(s)")
    log.info(f"Kept (no match):        {skipped:,} file(s)")
    if errors:
        log.warning(f"Errors:                 {errors:,} file(s) — check log above")
    if not dry_run:
        log.info(f"Trash location:         {TRASH_DIR}")


if __name__ == "__main__":
    main()
    # remove_empty_dirs(OLD_DIR, False)