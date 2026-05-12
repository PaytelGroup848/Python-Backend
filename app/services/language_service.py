from langdetect import detect

from deep_translator import GoogleTranslator


SUPPORTED_LANGUAGES = {
    "en": "english",
    "hi": "hindi",
    "bn": "bengali",
    "ta": "tamil",
    "te": "telugu",
    "mr": "marathi"
}


def detect_language(text: str):

    try:

        lang = detect(text)

        return lang

    except Exception:

        return "en"


def translate_to_english(text: str):

    return GoogleTranslator(
        source="auto",
        target="en"
    ).translate(text)


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