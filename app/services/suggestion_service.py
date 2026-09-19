import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

MAX_SUGGESTIONS = 4

# Structural prefix regex: requires a delimiter (: . -) immediately after the prefix keyword
# Matches:
#   - Suggestion 1:
#   * Suggestion:
#   - **Suggestion 1:**
#   - Follow-up:
#   - Follow up:
#   - Q1:
#   - Question 1:
#   - Prompt 1:
#   - 1. 1.
# Does NOT match:
#   - Why is this a suggestion?
#   - What question should I ask?
STRUCTURAL_PREFIX_REGEX = re.compile(
    r'^[-*•]\s*(?:(?:\*{0,2}|_{0,2})(?:suggestion|follow-?up|follow\s+up|q|question|prompt)\s*\d*(?:\*{0,2}|_{0,2})\s*[:.-]\s*)+',
    re.IGNORECASE
)

REPEATED_NUMERIC_PREFIX_REGEX = re.compile(r'^(?:[-*•]\s*)?(?:\d+[\.\)]\s*)+')

TRAILING_SUGGESTIONS_BLOCK_REGEX = re.compile(
    r'(?:\r?\n){1,2}(?:(?:#{1,4}\s*)?\*{0,2}💡\s*(?:Follow-up\s+)?Suggestions:?\*{0,2}|(?:#{1,4}\s*|\*{1,2})(?:Follow-up\s+)?Suggestions:?\*{0,2}|(?:Follow-up\s+)?Suggestions:)\s*(?:\r?\n)([\s\S]*)$',
    re.IGNORECASE
)


def normalize_comparison_key(text: str) -> str:
    """
    Generates a normalized comparison key for exact deduplication.
    Lowercases, collapses internal whitespace, and trims trailing punctuation.
    """
    cleaned = text.lower()
    cleaned = re.sub(r'[\s\?\.!,-]+$', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def clean_suggestion_item(raw_line: str) -> str | None:
    """
    Cleans a single candidate suggestion line according to the canonical contract.
    Preserves display casing and legitimate language ('very very', 'bye bye').
    Returns None if the line is invalid or empty.
    """
    if not raw_line or not isinstance(raw_line, str):
        return None

    line = raw_line.strip()
    if not line:
        return None

    # Step 1: Strip structural model prefixes (delimiter-guarded)
    line = STRUCTURAL_PREFIX_REGEX.sub('', line).strip()

    # Step 2: Strip repeated numeric bullets (e.g. "1. 1. Question")
    line = REPEATED_NUMERIC_PREFIX_REGEX.sub('', line).strip()

    # Step 3: Strip leading bullet symbols if any remain
    line = re.sub(r'^[-*•]\s*', '', line).strip()

    # Step 4: Strip surrounding markdown quotes, asterisks, backticks
    line = re.sub(r'^[\s*"\'_`]+|[\s*"\'_`]+$', '', line).strip()

    # Step 5: Collapse internal whitespace
    line = re.sub(r'\s+', ' ', line).strip()

    # Step 6: Validate length and emptiness
    if not line or len(line) > 120:
        return None

    return line


def extract_and_normalize_suggestions(raw_text: str) -> Tuple[str, List[str]]:
    """
    Fail-Safe Canonical Suggestion Extractor & Normalizer.

    Contract:
      - Detects trailing suggestion block outside code fences.
      - If block NOT found: returns (raw_text, []).
      - If block found: slices only the identified trailing block from assistant body,
        and normalizes candidate items up to MAX_SUGGESTIONS (4).
      - If any internal exception occurs: returns (raw_text, []) safely without corrupting primary content.
    """
    if not raw_text or not isinstance(raw_text, str):
        return raw_text or "", []

    try:
        # Check if index is inside a markdown code fence
        code_blocks = [m.span() for m in re.finditer(r'```[\s\S]*?```', raw_text)]

        match = None
        for m in TRAILING_SUGGESTIONS_BLOCK_REGEX.finditer(raw_text):
            start = m.start()
            if not any(cb_start <= start < cb_end for cb_start, cb_end in code_blocks):
                match = m

        if not match:
            return raw_text, []

        raw_block = match.group(1) or ""
        raw_lines = [l.strip() for l in raw_block.splitlines() if l.strip()]

        if not raw_lines:
            # Block header exists but empty: cleanly strip the header from body
            clean_body = raw_text[:match.start()].rstrip()
            return clean_body, []

        canonical_list: List[str] = []
        seen_keys = set()

        for line in raw_lines:
            # Filter out standalone empty bullet marks like "-" or "*"
            if re.match(r'^[-*•]$', line):
                continue

            cleaned_item = clean_suggestion_item(line)
            if not cleaned_item:
                continue

            comparison_key = normalize_comparison_key(cleaned_item)
            if not comparison_key or comparison_key in seen_keys:
                continue

            seen_keys.add(comparison_key)
            canonical_list.append(cleaned_item)

            if len(canonical_list) >= MAX_SUGGESTIONS:
                break

        clean_body = raw_text[:match.start()].rstrip()
        return clean_body, canonical_list

    except Exception as exc:
        logger.warning(f"suggestion_parser_failed: {exc}")
        # Invariant #9: Parser failure must never corrupt or truncate the assistant's primary response
        return raw_text, []


def clean_legacy_memory_text(text: str) -> str:
    """
    Targeted Legacy Memory Cleaner.
    Strips recognized trailing suggestion blocks from historical session messages
    before constructing conversation memory prompt context.
    Never strips legitimate prose containing the word 'Suggestions'.
    """
    if not text or not isinstance(text, str):
        return text or ""

    try:
        code_blocks = [m.span() for m in re.finditer(r'```[\s\S]*?```', text)]

        match = None
        for m in TRAILING_SUGGESTIONS_BLOCK_REGEX.finditer(text):
            start = m.start()
            if not any(cb_start <= start < cb_end for cb_start, cb_end in code_blocks):
                match = m

        if match:
            return text[:match.start()].rstrip()

        return text
    except Exception as exc:
        logger.warning(f"legacy_memory_cleaner_failed: {exc}")
        return text
