"""
word6_crack.py — Word 6.0 / Word 95 (.doc) password cracker and text extractor.

Supports five attack strategies:
  1. xor          — frequency-analysis XOR key recovery + extract (default)
  2. crib         — known-plaintext / crib-drag attack using guessed words
  3. brute        — msoffcrypto brute-force with prefix/suffix wordlist
  4. really_brute — exhaustive character-space brute force, 1 up to N characters
  5. raw          — extract all Latin-1 readable strings without decryption

Also includes two diagnostic tools:
  - entropy     — measure stream entropy to distinguish encryption from corruption
  - text_offset — scan for the true start of text content inside the stream

To use: edit the CONFIG block below, then run:
    python word6_crack.py

Dependencies:
    pip install olefile msoffcrypto-tool
"""

import itertools
import math
import re
from collections import Counter
from pathlib import Path

import olefile

try:
    import msoffcrypto
    MSOFFCRYPTO_AVAILABLE = True
except ImportError:
    MSOFFCRYPTO_AVAILABLE = False


# ===========================================================================
# CONFIG — edit these values, then run the script
# ===========================================================================

DOC_FILE  = r"C:/Users/user/Documents/to_crack.doc"
OUT_FILE  = r"C:/Users/user/Documents/extracted.txt"

# Attack mode: "xor", "crib", "brute", "really_brute", or "raw"
# Diagnostic modes: "entropy", "text_offset"
MODE = "really_brute"

# --- XOR mode settings ---
# Set to None to auto-detect, or override with a known key length (e.g. 16)
XOR_KEY_LENGTH_OVERRIDE = None

# --- Crib-drag mode settings ---
# Words/phrases likely to appear in the plaintext (Dutch or English)
# Longer cribs give more key bytes per hit; try document-specific words too
CRIB_WORDS = [
    "de ", "het ", "een ", "en ", "van ", "in ", "is ", "op ", "dat ",
    "met ", "te ", "zijn ", "voor ", "niet ", "aan ", "er ", "maar ",
    " de ", " het ", " een ", " en ",
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
    "19", "20",  # year prefixes
]

# --- Brute-force mode settings ---
BRUTE_PREFIXES       = ["ABC", "AbC"]
BRUTE_SUFFIX_CHARS   = list("0123456789!@#$%")
BRUTE_MAX_SUFFIX_LEN = 4
BRUTE_EXTRA_PASSWORDS = [
    "", "1234", "password", "word",
    "user", "lastname", "firstname",
    "1993", "1994", "1995", "1996",
]


# --- really_brute mode settings ---
# Full character-space exhaustive search. WARNING: combinatorially expensive.
# 62 chars (a-z A-Z 0-9) at length 6 = 56 billion combinations.
# Use only when you have no clues about the password structure.
# Alphabet: a-z, A-Z, 0-9, and special characters
REALLY_BRUTE_CHARSET = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "!@#$%^&*()_-"
)
REALLY_BRUTE_MAX_LENGTH = 6   # WARNING: lengths > 6 will take extremely long
REALLY_BRUTE_START_LENGTH = 1  # start from this length (set higher to resume)

# --- text_offset mode settings ---
# Scan range when looking for the true text start offset
TEXT_OFFSET_SCAN_START = 0x000
TEXT_OFFSET_SCAN_END   = 0x800
TEXT_OFFSET_SCAN_STEP  = 0x010

# ===========================================================================
# END CONFIG
# ===========================================================================


WORD_DOCUMENT_STREAM = "WordDocument"
TEXT_STREAM_OFFSET   = 0x400   # Word 6.0 body starts after the 1 KB header
SPACE_BYTE           = 0x20    # most frequent byte in Dutch/English plain text
MIN_READABLE_RUN     = 15      # minimum chars to count as a readable chunk


# ---------------------------------------------------------------------------
# OLE helpers
# ---------------------------------------------------------------------------

def read_word_document_stream(doc_path: str) -> bytes:
    """Open a Word 6.0 OLE file and return the raw WordDocument stream bytes.

    Args:
        doc_path: Path to the .doc file.

    Returns:
        Raw bytes of the WordDocument stream.

    Raises:
        FileNotFoundError: If the file does not exist.
        KeyError: If the WordDocument stream is absent.
    """
    path = Path(doc_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {doc_path}")
    with olefile.OleFileIO(str(path)) as ole:
        if not ole.exists(WORD_DOCUMENT_STREAM):
            raise KeyError(
                f"Stream '{WORD_DOCUMENT_STREAM}' not found — "
                "is this really a Word 6.0/95 file?"
            )
        return ole.openstream(WORD_DOCUMENT_STREAM).read()


def list_ole_streams(doc_path: str) -> list[str]:
    """Return the names of all OLE streams present in the file.

    Args:
        doc_path: Path to the .doc file.

    Returns:
        List of stream name strings.
    """
    with olefile.OleFileIO(doc_path) as ole:
        return ["/".join(entry) for entry in ole.listdir()]


# ---------------------------------------------------------------------------
# Diagnostic: entropy analysis
# ---------------------------------------------------------------------------

def compute_byte_entropy(data: bytes) -> float:
    """Compute Shannon entropy of a byte sequence (bits per byte, 0–8).

    Reference values:
      ~7.9–8.0  → modern AES encryption (near-random)
      ~6.0–7.5  → XOR obfuscation like Word 6.0 (structured but scrambled)
      ~4.0–5.5  → plain natural-language text
      ~0.0–3.0  → highly repetitive / mostly-zero data

    Args:
        data: Byte sequence to analyse.

    Returns:
        Shannon entropy in bits per byte.
    """
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    return -sum(
        (c / total) * math.log2(c / total)
        for c in counts.values()
        if c > 0
    )


def run_entropy_analysis(doc_path: str) -> None:
    """Print entropy of the full stream and its major sub-sections.

    Useful for distinguishing XOR obfuscation (~6–7.5 bits) from real AES
    encryption (~7.9–8.0 bits) and from corruption or empty space (~0–3 bits).

    Args:
        doc_path: Path to the .doc file.
    """
    print(f"\n=== Entropy Analysis: {doc_path} ===\n")
    stream = read_word_document_stream(doc_path)

    sections = [
        ("Full stream",         stream),
        ("Header (0x000–0x400)", stream[:0x400]),
        ("Body   (0x400–end)",  stream[0x400:]),
        ("First 1 KB of body",  stream[0x400:0x800]),
    ]

    for label, data in sections:
        entropy = compute_byte_entropy(data)
        if entropy > 7.8:
            verdict = "→ looks like strong encryption (AES/RC4)"
        elif entropy > 5.5:
            verdict = "→ looks like XOR obfuscation (Word 6.0 style)"
        elif entropy > 3.0:
            verdict = "→ looks like plain text or light encoding"
        else:
            verdict = "→ mostly empty / repetitive / corrupt"
        print(f"  {label:<30} {entropy:.3f} bits/byte  {verdict}")


# ---------------------------------------------------------------------------
# Diagnostic: locate the true text start offset
# ---------------------------------------------------------------------------

def run_text_offset_scan(doc_path: str, key: bytes | None = None) -> None:
    """Scan the stream at multiple offsets to find where readable text begins.

    Optionally decrypts with a known key before scanning. Useful when the
    standard 0x400 offset gives garbled output and the true body offset
    needs to be found empirically.

    Args:
        doc_path: Path to the .doc file.
        key: Optional XOR key to apply before scanning.
    """
    print(f"\n=== Text Offset Scan: {doc_path} ===\n")
    stream = read_word_document_stream(doc_path)

    for offset in range(TEXT_OFFSET_SCAN_START, TEXT_OFFSET_SCAN_END, TEXT_OFFSET_SCAN_STEP):
        segment = stream[offset:offset + 128]
        if key:
            segment = bytes(segment[i] ^ key[i % len(key)] for i in range(len(segment)))
        readable = re.findall(rb"[A-Za-z\xc0-\xff\x20-\x7e]{4,}", segment)
        total_readable = sum(len(r) for r in readable)
        ratio = total_readable / len(segment) if segment else 0
        bar = "#" * int(ratio * 40)
        print(f"  0x{offset:04x}  {ratio:5.1%}  [{bar:<40}]  {readable[:2]}")


# ---------------------------------------------------------------------------
# XOR frequency-analysis attack
# ---------------------------------------------------------------------------

def detect_xor_key_length(ciphertext: bytes, max_len: int = 32) -> int:
    """Estimate XOR key length via coincidence counting (Kasiski method).

    Counts positions where ciphertext[i] == ciphertext[i+L] for each candidate
    length L. A strong spike in the score indicates the true key length.

    Args:
        ciphertext: Encrypted bytes (header already stripped).
        max_len: Maximum key length to test.

    Returns:
        Most likely key length.
    """
    scores = {
        keylen: sum(
            ciphertext[i] == ciphertext[i + keylen]
            for i in range(len(ciphertext) - keylen)
        )
        for keylen in range(1, max_len + 1)
    }
    best = max(scores, key=lambda k: scores[k])
    print("Key length coincidence scores:")
    for k, v in sorted(scores.items()):
        marker = " <-- best" if k == best else ""
        print(f"  Length {k:2d}: {v:6d} matches{marker}")
    return best


def recover_xor_key(ciphertext: bytes, key_length: int) -> bytes:
    """Recover each byte of the XOR key via frequency analysis.

    Assumes the most common byte in each key-position column corresponds to
    an encrypted space (0x20), the most frequent character in Dutch/English prose.

    Args:
        ciphertext: Encrypted bytes (header stripped).
        key_length: Known or estimated key length.

    Returns:
        The recovered key as bytes.
    """
    key = bytearray(key_length)
    for i in range(key_length):
        column = bytes(ciphertext[j] for j in range(i, len(ciphertext), key_length))
        most_common_byte = Counter(column).most_common(1)[0][0]
        key[i] = most_common_byte ^ SPACE_BYTE

    print(f"\nRecovered XOR key ({key_length} bytes):")
    print(f"  Hex   : {bytes(key).hex()}")
    print(f"  ASCII : {''.join(chr(b) if 32 <= b < 127 else '?' for b in key)}")
    return bytes(key)


def decrypt_xor(ciphertext: bytes, key: bytes) -> bytes:
    """XOR-decrypt a byte stream with a repeating key.

    Args:
        ciphertext: Encrypted bytes.
        key: The repeating XOR key.

    Returns:
        Decrypted bytes.
    """
    key_len = len(key)
    return bytes(ciphertext[i] ^ key[i % key_len] for i in range(len(ciphertext)))


def run_xor_attack(doc_path: str, out_file: str, key_length_override: int | None) -> None:
    """Full XOR pipeline: detect key length → recover key → decrypt → save.

    Args:
        doc_path: Path to the encrypted .doc file.
        out_file: Path to write the recovered text.
        key_length_override: If set, skips auto-detection and uses this length.
    """
    print(f"\n=== XOR Attack: {doc_path} ===\n")
    stream = read_word_document_stream(doc_path)
    ciphertext = stream[TEXT_STREAM_OFFSET:]

    key_length = key_length_override or detect_xor_key_length(ciphertext)
    key = recover_xor_key(ciphertext, key_length)
    decrypted = decrypt_xor(ciphertext, key)

    chunks = extract_readable_chunks(decrypted)
    print(f"\nExtracted {len(chunks)} readable chunks.")
    if chunks:
        print("\n--- First 5 chunks ---")
        for chunk in chunks[:5]:
            print(repr(chunk))

    save_text_output(chunks, out_file)


# ---------------------------------------------------------------------------
# Crib-drag (known-plaintext) attack
# ---------------------------------------------------------------------------

def crib_drag(ciphertext: bytes, crib: str, key_length: int) -> dict[int, bytes]:
    """Slide a known-plaintext crib across the ciphertext to recover key bytes.

    For each offset where the crib is tried, XOR the crib against the
    ciphertext to produce candidate key bytes at those positions. Votes are
    accumulated across all offsets; positions with consistent votes are likely
    correct key bytes.

    Args:
        ciphertext: Encrypted bytes (header stripped).
        crib: Known or guessed plaintext string.
        key_length: Estimated key length (used to map positions back to key slots).

    Returns:
        Dict mapping key byte index (0 to key_length-1) to a Counter of candidate
        values, sorted by vote count descending.
    """
    crib_bytes = crib.encode("latin-1")
    crib_len = len(crib_bytes)
    votes: dict[int, Counter] = {i: Counter() for i in range(key_length)}

    for offset in range(len(ciphertext) - crib_len):
        for j, cb in enumerate(crib_bytes):
            key_pos = (offset + j) % key_length
            candidate = ciphertext[offset + j] ^ cb
            votes[key_pos][candidate] += 1

    return {pos: counter for pos, counter in votes.items()}


def run_crib_attack(
    doc_path: str,
    out_file: str,
    cribs: list[str],
    key_length_override: int | None,
) -> None:
    """Known-plaintext crib-drag attack: combine votes from multiple cribs.

    For each crib word, slide it across the ciphertext and accumulate votes
    for each key byte position. The most-voted candidate per position forms
    the key. Falls back to frequency analysis for positions with no crib coverage.

    Args:
        doc_path: Path to the encrypted .doc file.
        out_file: Path to write the recovered text.
        cribs: List of words/phrases likely present in the plaintext.
        key_length_override: Override key length (None = auto-detect).
    """
    print(f"\n=== Crib-Drag Attack: {doc_path} ===\n")
    stream = read_word_document_stream(doc_path)
    ciphertext = stream[TEXT_STREAM_OFFSET:]

    key_length = key_length_override or detect_xor_key_length(ciphertext)
    print(f"\nUsing key length: {key_length}")

    # Accumulate votes across all cribs
    combined_votes: dict[int, Counter] = {i: Counter() for i in range(key_length)}
    for crib in cribs:
        votes = crib_drag(ciphertext, crib, key_length)
        for pos, counter in votes.items():
            combined_votes[pos].update(counter)

    # Build key from top votes; fall back to frequency analysis for low-confidence positions
    freq_key = recover_xor_key(ciphertext, key_length)
    key = bytearray(key_length)
    print("\nKey recovery (crib votes vs frequency fallback):")
    for pos in range(key_length):
        top = combined_votes[pos].most_common(1)
        if top and top[0][1] > 5:
            key[pos] = top[0][0]
            source = f"crib ({top[0][1]} votes)"
        else:
            key[pos] = freq_key[pos]
            source = "frequency fallback"
        print(f"  Position {pos:2d}: 0x{key[pos]:02x}  ({source})")

    print(f"\nFinal key hex: {bytes(key).hex()}")

    decrypted = decrypt_xor(ciphertext, bytes(key))
    chunks = extract_readable_chunks(decrypted)
    print(f"\nExtracted {len(chunks)} readable chunks.")
    if chunks:
        print("\n--- First 5 chunks ---")
        for chunk in chunks[:5]:
            print(repr(chunk))

    save_text_output(chunks, out_file)


# ---------------------------------------------------------------------------
# Brute-force attack via msoffcrypto
# ---------------------------------------------------------------------------

def attempt_msoffcrypto_decrypt(doc_path: str, out_file: str, password: str) -> bool:
    """Try to decrypt the file with msoffcrypto using the given password.

    Args:
        doc_path: Path to the encrypted .doc file.
        out_file: Path to write the decrypted file on success.
        password: Password to attempt.

    Returns:
        True if decryption succeeded, False otherwise.
    """
    if not MSOFFCRYPTO_AVAILABLE:
        raise ImportError("msoffcrypto-tool not installed. Run: pip install msoffcrypto-tool")
    try:
        with open(doc_path, "rb") as f:
            office_file = msoffcrypto.OfficeFile(f)
            office_file.load_key(password=password)
            with open(out_file, "wb") as out:
                office_file.decrypt(out)
        return True
    except Exception:
        return False


def generate_password_candidates(
    prefixes: list[str],
    suffix_chars: list[str],
    max_suffix_length: int,
    extra_passwords: list[str],
) -> list[str]:
    """Build an ordered list of password candidates, shortest suffixes first.

    Order: extra_passwords → prefix alone → prefix+1char → prefix+2chars → …

    Args:
        prefixes: Known/guessed password prefixes.
        suffix_chars: Alphabet of characters to append.
        max_suffix_length: Maximum number of suffix characters to try.
        extra_passwords: Additional passwords prepended to the list.

    Returns:
        Ordered list of candidate strings.
    """
    candidates: list[str] = list(extra_passwords)
    for prefix in prefixes:
        for length in range(0, max_suffix_length + 1):
            for combo in itertools.product(suffix_chars, repeat=length):
                candidates.append(prefix + "".join(combo))
    return candidates


def run_brute_force_attack(
    doc_path: str,
    out_file: str,
    prefixes: list[str],
    suffix_chars: list[str],
    max_suffix_length: int,
    extra_passwords: list[str],
) -> None:
    """Brute-force the password using msoffcrypto with a generated candidate list.

    Args:
        doc_path: Path to the encrypted .doc file.
        out_file: Path to write the decrypted file on success.
        prefixes: Known/guessed password prefixes.
        suffix_chars: Alphabet of suffix characters to combine.
        max_suffix_length: Maximum suffix characters to append per prefix.
        extra_passwords: Additional passwords to try before the generated list.
    """
    print(f"\n=== Brute-Force Attack: {doc_path} ===\n")
    candidates = generate_password_candidates(
        prefixes, suffix_chars, max_suffix_length, extra_passwords
    )
    print(f"Trying {len(candidates):,} password candidates...")

    for i, pwd in enumerate(candidates):
        if i % 500 == 0 and i > 0:
            print(f"  ... {i:,} tried (last: {pwd!r})")
        if attempt_msoffcrypto_decrypt(doc_path, out_file, pwd):
            print(f"\nSUCCESS — password is: {pwd!r}")
            print(f"Decrypted file saved to: {out_file}")
            return

    print("\nNo password found. Try more prefixes, suffix chars, or a higher max_suffix_length.")



# ---------------------------------------------------------------------------
# Really-brute: exhaustive full character-space attack
# ---------------------------------------------------------------------------

def run_really_brute_force_attack(
    doc_path: str,
    out_file: str,
    charset: str,
    max_length: int,
    start_length: int,
) -> None:
    """Exhaustive brute-force over the full character space, length by length.

    Tries every combination of characters from `charset` starting at
    `start_length` characters up to `max_length`. Shortest passwords first.

    Estimated scale (charset size 75):
      Length 1:            75 candidates
      Length 2:         5,625 candidates
      Length 3:       421,875 candidates
      Length 4:    31,640,625 candidates
      Length 5: 2,373,046,875 candidates  (~hours on a modern CPU)
      Length 6: 177 billion               (~days — consider hashcat instead)

    Args:
        doc_path: Path to the encrypted .doc file.
        out_file: Path to write the decrypted file on success.
        charset: String of all characters to include in the search.
        max_length: Maximum password length to try.
        start_length: Start from this length (useful to resume a stopped run).
    """
    if not MSOFFCRYPTO_AVAILABLE:
        raise ImportError("msoffcrypto-tool not installed. Run: pip install msoffcrypto-tool")

    charset_list = list(charset)
    charset_size = len(charset_list)
    print(f"\n=== Really-Brute Attack: {doc_path} ===")
    print(f"Charset : {charset!r} ({charset_size} chars)")
    print(f"Lengths : {start_length} to {max_length}")

    # Pre-calculate total for progress reporting
    total = sum(charset_size ** length for length in range(start_length, max_length + 1))
    print(f"Total candidates: {total:,}")
    if total > 10_000_000:
        print("WARNING: this will take a very long time. Consider using hashcat for lengths > 5.")
    print()

    tried = 0
    for length in range(start_length, max_length + 1):
        count_this_length = charset_size ** length
        print(f"Trying length {length} ({count_this_length:,} candidates)...")
        for combo in itertools.product(charset_list, repeat=length):
            pwd = "".join(combo)
            tried += 1
            if tried % 100_000 == 0:
                print(f"  ... {tried:,} tried / {total:,} total ({100*tried/total:.2f}%)  last: {pwd!r}")
            if attempt_msoffcrypto_decrypt(doc_path, out_file, pwd):
                print(f"\nSUCCESS — password is: {pwd!r}")
                print(f"Decrypted file saved to: {out_file}")
                return
        print(f"  Length {length} exhausted, no match.")

    print(f"\nExhausted all {tried:,} candidates up to length {max_length}. Password not found.")
    print("Consider increasing REALLY_BRUTE_MAX_LENGTH or using hashcat for longer passwords.")

# ---------------------------------------------------------------------------
# Raw extraction (no key required)
# ---------------------------------------------------------------------------

def run_raw_extraction(doc_path: str, out_file: str) -> None:
    """Extract all readable Latin-1 strings from the raw stream without decryption.

    Useful as a fallback when no key is known. Returns partial/scrambled content
    for encrypted files but may recover metadata or unencrypted fragments.

    Args:
        doc_path: Path to the .doc file.
        out_file: Path to write the extracted text.
    """
    print(f"\n=== Raw Extraction: {doc_path} ===\n")
    stream = read_word_document_stream(doc_path)
    chunks = extract_readable_chunks(stream, min_length=8)
    print(f"Extracted {len(chunks)} readable chunks (no decryption).")
    save_text_output(chunks, out_file)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def extract_readable_chunks(data: bytes, min_length: int = MIN_READABLE_RUN) -> list[str]:
    """Extract runs of readable Latin-1 text from a byte stream.

    Args:
        data: Raw or decrypted bytes.
        min_length: Minimum run length to include.

    Returns:
        List of readable text strings.
    """
    pattern = (
        rb"[A-Za-z\xc0-\xff\x20-\x7e,\.!?;:\'\"\(\)\-]{"
        + str(min_length).encode()
        + rb",}"
    )
    return [
        chunk.decode("latin-1", errors="replace").strip()
        for chunk in re.findall(pattern, data)
        if len(chunk.strip()) >= min_length
    ]


def save_text_output(chunks: list[str], out_file: str) -> None:
    """Write extracted text chunks to a UTF-8 text file.

    Args:
        chunks: List of readable text strings.
        out_file: Destination file path.
    """
    path = Path(out_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(chunk + "\n\n")
    print(f"\nOutput saved to: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the selected attack or diagnostic mode using the CONFIG values."""
    print(f"File   : {DOC_FILE}")
    print(f"Output : {OUT_FILE}")
    print(f"Mode   : {MODE}")

    try:
        streams = list_ole_streams(DOC_FILE)
        print(f"Streams: {streams}")
    except Exception as e:
        print(f"Warning: could not list OLE streams — {e}")

    if MODE == "xor":
        run_xor_attack(DOC_FILE, OUT_FILE, XOR_KEY_LENGTH_OVERRIDE)

    elif MODE == "crib":
        run_crib_attack(DOC_FILE, OUT_FILE, CRIB_WORDS, XOR_KEY_LENGTH_OVERRIDE)

    elif MODE == "brute":
        run_brute_force_attack(
            doc_path=DOC_FILE,
            out_file=OUT_FILE,
            prefixes=BRUTE_PREFIXES,
            suffix_chars=BRUTE_SUFFIX_CHARS,
            max_suffix_length=BRUTE_MAX_SUFFIX_LEN,
            extra_passwords=BRUTE_EXTRA_PASSWORDS,
        )

    elif MODE == "really_brute":
        run_really_brute_force_attack(
            doc_path=DOC_FILE,
            out_file=OUT_FILE,
            charset=REALLY_BRUTE_CHARSET,
            max_length=REALLY_BRUTE_MAX_LENGTH,
            start_length=REALLY_BRUTE_START_LENGTH,
        )

    elif MODE == "raw":
        run_raw_extraction(DOC_FILE, OUT_FILE)

    elif MODE == "entropy":
        run_entropy_analysis(DOC_FILE)

    elif MODE == "text_offset":
        run_text_offset_scan(DOC_FILE)

    else:
        print(f"Unknown mode: {MODE!r}. Choose: xor, crib, brute, really_brute, raw, entropy, text_offset.")


if __name__ == "__main__":
    main()