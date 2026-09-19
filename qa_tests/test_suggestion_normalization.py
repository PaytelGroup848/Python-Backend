import pytest
from app.services.suggestion_service import (
    clean_suggestion_item,
    extract_and_normalize_suggestions,
    clean_legacy_memory_text,
    normalize_comparison_key,
    MAX_SUGGESTIONS,
)


def test_clean_suggestion_item_prefixes():
    prefix_test_cases = [
        ("- Suggestion 1: How do lists work?", "How do lists work?"),
        ("* Suggestion 1: How do lists work?", "How do lists work?"),
        ("- **Suggestion 1:** What is async?", "What is async?"),
        ("- Follow-up: Compare sets and lists", "Compare sets and lists"),
        ("- Follow up: Compare sets and lists", "Compare sets and lists"),
        ("- Q1: What is immutability?", "What is immutability?"),
        ("- Question 1: What is GIL?", "What is GIL?"),
        ("- Prompt 1: Explain recursion", "Explain recursion"),
        ("- 1. 1. What is recursion?", "What is recursion?"),
        ("- Suggestion: Why is this a suggestion?", "Why is this a suggestion?"),
        ("- Question: What question should I ask?", "What question should I ask?"),
        ('- "What is immutability?"', "What is immutability?"),
        ("- `Explain async/await`", "Explain async/await"),
    ]

    for raw, expected in prefix_test_cases:
        cleaned = clean_suggestion_item(raw)
        assert cleaned == expected, f"Failed for raw input: '{raw}', expected: '{expected}', got: '{cleaned}'"


def test_false_positive_preservation():
    """
    Ensures that natural language containing prefix keywords or repetitive words
    is NEVER damaged or stripped.
    """
    false_positives = [
        ("- Why is this a suggestion?", "Why is this a suggestion?"),
        ("- What question should I ask?", "What question should I ask?"),
        ("- Why is this very very important?", "Why is this very very important?"),
        ("- How to say bye bye in Spanish?", "How to say bye bye in Spanish?"),
        ("- Can a robot go go?", "Can a robot go go?"),
        ("- ha ha that was funny", "ha ha that was funny"),
    ]

    for raw, expected in false_positives:
        cleaned = clean_suggestion_item(raw)
        assert cleaned == expected, f"False positive damaged for: '{raw}', got: '{cleaned}'"


def test_normalized_deduplication():
    """
    Asserts exact normalized deduplication: case-insensitivity, whitespace,
    and trailing punctuation variations are collapsed, while preserving original casing.
    """
    sample = (
        "Python has many powerful features.\n\n"
        "**💡 Suggestions:**\n"
        "- How can I learn Python?\n"
        "- how can i learn python?\n"
        "- How can I learn Python ?\n"
        "- How can I learn Python!\n"
    )
    clean_body, suggestions = extract_and_normalize_suggestions(sample)
    assert clean_body == "Python has many powerful features."
    assert len(suggestions) == 1
    assert suggestions[0] == "How can I learn Python?"


def test_semantic_near_duplicates_preserved():
    """
    Ensures semantically similar but non-identical questions are BOTH preserved.
    No destructive semantic deduplication.
    """
    sample = (
        "Here is the explanation.\n\n"
        "**💡 Suggestions:**\n"
        "- How can I learn Python?\n"
        "- How do I start learning Python?\n"
    )
    _, suggestions = extract_and_normalize_suggestions(sample)
    assert len(suggestions) == 2
    assert "How can I learn Python?" in suggestions
    assert "How do I start learning Python?" in suggestions


def test_max_suggestions_cap():
    """
    Verifies that suggestions are capped at MAX_SUGGESTIONS = 4.
    """
    sample = (
        "Explanation text.\n\n"
        "**💡 Suggestions:**\n"
        "- Question 1\n"
        "- Question 2\n"
        "- Question 3\n"
        "- Question 4\n"
        "- Question 5\n"
        "- Question 6\n"
    )
    _, suggestions = extract_and_normalize_suggestions(sample)
    assert len(suggestions) == MAX_SUGGESTIONS
    assert len(suggestions) == 4


def test_parser_exception_failsafe(monkeypatch):
    """
    Invariant #9: Parser exception must NEVER corrupt or truncate the assistant's primary response.
    """
    raw_response = (
        "Normal assistant answer.\n\n"
        "```python\n"
        "for i in range(2):\n"
        "    print('hello')\n"
        "```\n\n"
        "**💡 Suggestions:**\n"
        "- Suggestion 1: Explain this code\n"
    )

    # Force clean_suggestion_item to raise an unexpected runtime error
    def broken_cleaner(*args, **kwargs):
        raise RuntimeError("Injected unexpected parser failure")

    import app.services.suggestion_service as ss
    monkeypatch.setattr(ss, "clean_suggestion_item", broken_cleaner)

    clean_body, suggestions = ss.extract_and_normalize_suggestions(raw_response)
    # Primary response is 100% preserved
    assert clean_body == raw_response
    assert suggestions == []


def test_code_block_preservation():
    """
    Invariant #2: Code blocks are never modified.
    """
    raw_response = (
        "Here is the code solution:\n\n"
        "```python\n"
        "for i in range(2):\n"
        "    print('hello')\n"
        "```\n\n"
        "**💡 Suggestions:**\n"
        "- How do I optimize this loop?\n"
        "- Explain range in Python\n"
    )
    clean_body, suggestions = extract_and_normalize_suggestions(raw_response)
    assert "for i in range(2):\n    print('hello')" in clean_body
    assert len(suggestions) == 2


def test_legacy_memory_cleaner_targeted_only():
    """
    Invariant #4: Legacy memory cleaner strips recognized trailing blocks only,
    never corrupting legitimate body prose containing the word 'Suggestions'.
    """
    prose_with_word = "Suggestions are useful when building interactive AI chatbots for users."
    cleaned = clean_legacy_memory_text(prose_with_word)
    assert cleaned == prose_with_word

    legacy_message = (
        "Python is dynamically typed.\n\n"
        "**💡 Suggestions:**\n"
        "- What is type hinting?\n"
        "- Explain mypy\n"
    )
    cleaned_legacy = clean_legacy_memory_text(legacy_message)
    assert cleaned_legacy == "Python is dynamically typed."
