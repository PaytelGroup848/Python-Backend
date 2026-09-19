import pytest
from app.services.language_service import (
    detect_language_and_script,
    get_language_directive,
)
from app.services.agent_service import (
    ContextBuilderService,
    LanguagePipeline,
)


def test_detect_hinglish_queries():
    hinglish_samples = [
        "bhai list aur tuple me kya farq hai",
        "ye API kaise kaam karti hai thoda explain karo",
        "kya hum python se direct database connect kar sakte hain?",
        "mujhe ek simple code example do",
        "kaise ho bhai sab badhiya?",
        "iss issue ko fix kaise kare",
        "mera server bar bar crash ho rha hai",
        "kuch edit mat karna exact batao",
    ]
    for query in hinglish_samples:
        detected = detect_language_and_script(query)
        assert detected["type"] == "hinglish", f"Failed for query: {query}, got: {detected}"
        assert detected["label"] == "Romanized Hinglish"
        assert detected["code"] == "hi-Latn"


def test_detect_devanagari_hindi_queries():
    hindi_samples = [
        "नमस्ते, आप कैसे हैं?",
        "पायथन में लिस्ट और टुपल में क्या अंतर है?",
        "डेटाबेस कनेक्शन कैसे ठीक करें?",
        "कृत्रिम बुद्धिमत्ता क्या है?",
    ]
    for query in hindi_samples:
        detected = detect_language_and_script(query)
        assert detected["type"] == "hindi_devanagari", f"Failed for query: {query}, got: {detected}"
        assert detected["label"] == "Devanagari Hindi"
        assert detected["code"] == "hi"


def test_detect_regional_queries():
    bengali = "কেমন আছেন? আমাকে পাইথন সম্পর্কে বলুন।"
    tamil = "வணக்கம் எப்படி இருக்கிறீர்கள்?"
    telugu = "నమస్కారం ఎలా ఉన్నారు?"

    assert detect_language_and_script(bengali)["label"] == "Bengali"
    assert detect_language_and_script(tamil)["label"] == "Tamil"
    assert detect_language_and_script(telugu)["label"] == "Telugu"


def test_detect_pure_english_queries():
    english_samples = [
        "What is the difference between a list and a tuple in Python?",
        "How do I optimize database connection pooling in async SQLAlchemy?",
        "Write a Dockerfile for a FastAPI application with Celery worker.",
        "Explain quantum computing in simple terms.",
        "The quick brown fox jumps over the lazy dog.",
    ]
    for query in english_samples:
        detected = detect_language_and_script(query)
        assert detected["type"] == "english", f"Failed for query: {query}, got: {detected}"
        assert detected["label"] == "English"
        assert detected["code"] == "en"


def test_explicit_user_override():
    samples = [
        ("Explain quantum mechanics in Hindi", "hindi_devanagari"),
        ("Explain this in Hinglish please", "hinglish"),
        ("Reply in English", "english"),
        ("हिंदी में समझाओ", "hindi_devanagari"),
    ]
    for query, expected_type in samples:
        detected = detect_language_and_script(query)
        assert detected["type"] == expected_type, f"Failed override for: {query}"


def test_get_language_directive_hinglish():
    detected = {"type": "hinglish", "label": "Romanized Hinglish"}
    directive = get_language_directive(detected)
    assert "CRITICAL MANDATORY DIRECTIVE: RESPOND IN NATURAL ROMANIZED HINGLISH" in directive
    assert "STRICT PROHIBITION: Do NOT write your response in pure English" in directive
    assert "STRICT PROHIBITION: Do NOT write in Devanagari script" in directive
    assert "MANDATORY SUGGESTIONS" in directive


def test_get_language_directive_hindi():
    detected = {"type": "hindi_devanagari", "label": "Devanagari Hindi"}
    directive = get_language_directive(detected)
    assert "CRITICAL MANDATORY DIRECTIVE: RESPOND IN DEVANAGARI HINDI" in directive
    assert "STRICT PROHIBITION: Do NOT reply in English" in directive


def test_context_builder_build_prompt_hinglish():
    query = "bhai list aur tuple me kya farq hai"
    prompt = ContextBuilderService.build_prompt(query=query)

    assert "CRITICAL MANDATORY DIRECTIVE: RESPOND IN NATURAL ROMANIZED HINGLISH" in prompt
    assert "ANSWER (ROMANIZED HINGLISH):\n" in prompt
    assert "target language: Romanized Hinglish" in prompt


def test_context_builder_build_prompt_hindi():
    query = "नमस्ते, पायथन क्या है?"
    prompt = ContextBuilderService.build_prompt(query=query)

    assert "CRITICAL MANDATORY DIRECTIVE: RESPOND IN DEVANAGARI HINDI (हिंदी)" in prompt
    assert "ANSWER (DEVANAGARI HINDI):\n" in prompt
    assert "target language: Devanagari Hindi" in prompt


def test_context_builder_build_prompt_english():
    query = "Explain binary search tree."
    prompt = ContextBuilderService.build_prompt(query=query)

    assert "LANGUAGE DIRECTIVE: ENGLISH" in prompt
    assert "ANSWER (ENGLISH):\n" in prompt
    assert "target language: English" in prompt


@pytest.mark.asyncio
async def test_language_pipeline_process_input():
    query, lang = await LanguagePipeline.process_input("bhai ye kaise hoga")
    assert query == "bhai ye kaise hoga"
    assert lang == "hinglish"

    query, lang = await LanguagePipeline.process_input("Explain in English please")
    assert lang == "english"


@pytest.mark.asyncio
async def test_language_pipeline_process_output_clean_echo():
    raw_response = "ANSWER (ROMANIZED HINGLISH): Bhai, yeh simple sa function hai."
    cleaned = await LanguagePipeline.process_output(raw_response)
    assert cleaned == "Bhai, yeh simple sa function hai."

    normal_response = "Bhai, yeh bilkul sahi chal raha hai."
    assert await LanguagePipeline.process_output(normal_response) == normal_response

