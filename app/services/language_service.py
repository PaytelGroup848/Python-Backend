from langdetect import (
    detect,
    DetectorFactory
)

from deep_translator import (
    GoogleTranslator
)

DetectorFactory.seed = 0


SUPPORTED_LANGUAGES = {
    "en": "english",
    "hi": "hindi",
    "bn": "bengali",
    "ta": "tamil",
    "te": "telugu",
    "mr": "marathi"
}


# -----------------------------
# LANGUAGE DETECTION
# -----------------------------

def detect_language(text: str):

    try:

        text = text.strip()

        # -----------------------------
        # SHORT QUERY SAFETY
        # -----------------------------

        if len(text.split()) <= 3:

            ascii_chars = sum(
                c.isascii()
                for c in text
            )

            ratio = ascii_chars / max(len(text), 1)

            # Mostly English ASCII
            if ratio > 0.9:
                return "en"

        lang = detect(text)

        # Unsupported → fallback English
        if lang not in SUPPORTED_LANGUAGES:
            return "en"

        return lang

    except Exception:

        return "en"


# -----------------------------
# TRANSLATE TO ENGLISH
# -----------------------------

def translate_to_english(text: str):

    return GoogleTranslator(
        source="auto",
        target="en"
    ).translate(text)


# -----------------------------
# TRANSLATE RESPONSE
# -----------------------------

def translate_response(
    text: str,
    target_language: str
):

    if target_language == "en":

        return text

    return GoogleTranslator(
        source="en",
        target=target_language
    ).translate(text)