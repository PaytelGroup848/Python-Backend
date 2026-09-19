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


# -----------------------------------------------------------------------------
# LANGUAGE UTILITIES (OFFLINE / OUT-OF-BAND UTILITY MODULE)
# -----------------------------------------------------------------------------
# IMPORTANT: These helper utilities are strictly for offline tasks, analytics,
# or telemetry. They must NEVER be called from the live request/streaming
# inference path. Core inference is 100% LLM-native.
# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------
# SUB-MILLISECOND ENTERPRISE LANGUAGE & SCRIPT CLASSIFIER (ZERO-LATENCY)
# -----------------------------------------------------------------------------
import re

UNAMBIGUOUS_HINGLISH_WORDS = {
    # Greetings & Salutations
    "bhai", "bhaiya", "bro", "yaar", "yr", "dost", "namaste", "namaskar",
    # Question words
    "kya", "kyu", "kyun", "kaise", "kaisa", "kaisi", "kab", "kahan", "kidhar", "kaun", "kitna", "kitne", "kitni",
    # Pronouns
    "mujhe", "mera", "meri", "mere", "hum", "hume", "humein", "hamara", "hamare", "hamari",
    "tujhe", "tera", "teri", "tere", "tumhe", "tumhara", "tumhare", "tumhari",
    "aapko", "aapka", "aapke", "aapki", "isme", "usme", "iske", "uske", "iska", "uska", "iski", "uski",
    "isne", "usne", "inhone", "unhone", "apna", "apne", "apni",
    # Verbs / Actions
    "karo", "kare", "karein", "karna", "karte", "karti", "karta", "kiya", "kiye", "kijiye", "kijiyega",
    "batao", "bataiye", "samjhao", "samjha", "samjhi", "samjhe", "samjhana",
    "hoga", "hogi", "honge", "hona", "hota", "hoti", "hote", "hua", "hui", "hue",
    "chahiye", "chahta", "chahti", "chahte",
    "sakte", "sakti", "sakta", "sakenge",
    "raha", "rahi", "rahe", "rha", "rhi", "rhe",
    "aata", "aati", "aate", "aana", "aaye", "aaya", "aayi", "aayein",
    "jaise", "waise", "kuch", "sabse", "sabko", "wala", "wali", "wale",
    # Auxiliaries & Connectors
    "hai", "hain", "hoon", "tha", "thi",
    "mein", "lekin", "magar", "parantu", "kyunki", "isliye",
    # Negations & Confirmations
    "nahi", "nhi", "haan", "haa", "achha", "accha", "theek", "thik", "sahi",
    # Modifiers
    "pehle", "baad", "bohot", "bahut", "zyada", "jyada", "thoda", "thodi", "thode",
    "wapas", "phir", "fir", "dobara"
}

SECONDARY_HINGLISH_WORDS = {
    "ye", "yeh", "wo", "woh", "kar", "kr", "aur", "toh", "se", "pe"
}


def detect_language_and_script(text: str) -> dict:
    """
    Sub-millisecond regex & Unicode script classifier for user queries.
    Distinguishes:
      - 'hinglish': Romanized Hindi/Hinglish written in Latin script
      - 'hindi_devanagari': Native Hindi written in Devanagari script
      - 'regional': Native regional Indian scripts (Bengali, Tamil, Telugu, etc.)
      - 'english': Standard English queries
    """
    if not text or not text.strip():
        return {"type": "english", "label": "English", "code": "en"}

    clean_text = text.strip()
    lower_text = clean_text.lower()

    # 1. Explicit user instructions (Highest priority override)
    if re.search(r'\b(in\s+hinglish|hinglish\s+me|hinglish\s+mein|answer\s+in\s+hinglish|reply\s+in\s+hinglish)\b', lower_text):
        return {"type": "hinglish", "label": "Romanized Hinglish", "code": "hi-Latn"}
    if re.search(r'\b(in\s+hindi|hindi\s+me|hindi\s+mein|हिंदी\s+में|explain\s+in\s+hindi|reply\s+in\s+hindi)\b', lower_text):
        return {"type": "hindi_devanagari", "label": "Devanagari Hindi", "code": "hi"}
    if re.search(r'\b(in\s+english|english\s+me|english\s+mein|reply\s+in\s+english|explain\s+in\s+english)\b', lower_text):
        return {"type": "english", "label": "English", "code": "en"}
    if re.search(r'\b(in\s+bengali|বাংলায়)\b', lower_text):
        return {"type": "regional", "label": "Bengali", "code": "bn"}
    if re.search(r'\b(in\s+tamil|தமிழில்)\b', lower_text):
        return {"type": "regional", "label": "Tamil", "code": "ta"}
    if re.search(r'\b(in\s+telugu|తెలుగులో)\b', lower_text):
        return {"type": "regional", "label": "Telugu", "code": "te"}
    if re.search(r'\b(in\s+marathi|मराठीत)\b', lower_text):
        return {"type": "regional", "label": "Marathi", "code": "mr"}
    if re.search(r'\b(in\s+gujarati|ગુજરાતીમાં)\b', lower_text):
        return {"type": "regional", "label": "Gujarati", "code": "gu"}

    # 2. Native Non-Latin Unicode Script Checks
    devanagari_chars = sum(1 for c in clean_text if '\u0900' <= c <= '\u097F')
    bengali_chars = sum(1 for c in clean_text if '\u0980' <= c <= '\u09FF')
    tamil_chars = sum(1 for c in clean_text if '\u0B80' <= c <= '\u0BFF')
    telugu_chars = sum(1 for c in clean_text if '\u0C00' <= c <= '\u0C7F')
    gujarati_chars = sum(1 for c in clean_text if '\u0A80' <= c <= '\u0AFF')
    kannada_chars = sum(1 for c in clean_text if '\u0C80' <= c <= '\u0CFF')
    malayalam_chars = sum(1 for c in clean_text if '\u0D00' <= c <= '\u0D7F')
    arabic_chars = sum(1 for c in clean_text if '\u0600' <= c <= '\u06FF')

    total_alpha = sum(1 for c in clean_text if c.isalpha()) or 1

    if devanagari_chars >= 2 or (devanagari_chars / total_alpha) > 0.15:
        return {"type": "hindi_devanagari", "label": "Devanagari Hindi", "code": "hi"}
    if bengali_chars >= 2:
        return {"type": "regional", "label": "Bengali", "code": "bn"}
    if tamil_chars >= 2:
        return {"type": "regional", "label": "Tamil", "code": "ta"}
    if telugu_chars >= 2:
        return {"type": "regional", "label": "Telugu", "code": "te"}
    if gujarati_chars >= 2:
        return {"type": "regional", "label": "Gujarati", "code": "gu"}
    if kannada_chars >= 2:
        return {"type": "regional", "label": "Kannada", "code": "kn"}
    if malayalam_chars >= 2:
        return {"type": "regional", "label": "Malayalam", "code": "ml"}
    if arabic_chars >= 2:
        return {"type": "regional", "label": "Urdu/Arabic", "code": "ur"}

    # 3. Romanized Hinglish Word Detection
    words = re.findall(r'[a-zA-Z]+', lower_text)
    total_words = len(words)
    if total_words == 0:
        return {"type": "english", "label": "English", "code": "en"}

    primary_matches = [w for w in words if w in UNAMBIGUOUS_HINGLISH_WORDS]
    secondary_matches = [w for w in words if w in SECONDARY_HINGLISH_WORDS]
    total_matches = len(primary_matches) + (len(secondary_matches) * 0.5)

    if len(primary_matches) >= 1 or total_matches >= 1.5:
        return {"type": "hinglish", "label": "Romanized Hinglish", "code": "hi-Latn", "matches": primary_matches}

    return {"type": "english", "label": "English", "code": "en"}


def get_language_directive(detected: dict) -> str:
    """
    Builds the high-priority, authoritative language directive matching the detected user query.
    """
    lang_type = detected.get("type", "english")
    label = detected.get("label", "English")

    if lang_type == "hinglish":
        return (
            "======================================================================\n"
            "CRITICAL MANDATORY DIRECTIVE: RESPOND IN NATURAL ROMANIZED HINGLISH\n"
            "The user asked their question in Romanized Hinglish (Hindi written in the English/Latin alphabet).\n"
            "You MUST formulate your ENTIRE response in natural, conversational Romanized Hinglish (Latin alphabet).\n"
            "- Tone: Natural, friendly, conversational Hinglish (e.g. 'Bhai, list aur tuple me basic farq yeh hai ki list mutable hoti hai (isko modify kar sakte hain), jabki tuple immutable hota hai...').\n"
            "- Code & Tech Terms: Keep programming code syntax, variable names, and technical keywords in standard English (e.g. `list`, `tuple`, `async`, `database`), but explain all concepts, reasoning, and context in fluent Hinglish.\n"
            "- STRICT PROHIBITION: Do NOT write your response in pure English.\n"
            "- STRICT PROHIBITION: Do NOT write in Devanagari script (क, ख, ग).\n"
            "- MANDATORY SUGGESTIONS: The 3 to 5 follow-up suggestions at the very end MUST ALSO be in Romanized Hinglish.\n"
            "======================================================================"
        )

    if lang_type == "hindi_devanagari":
        return (
            "======================================================================\n"
            "CRITICAL MANDATORY DIRECTIVE: RESPOND IN DEVANAGARI HINDI (हिंदी)\n"
            "The user asked their question in Hindi (Devanagari script).\n"
            "You MUST formulate your ENTIRE response in natural, fluent Hindi in Devanagari script (हिंदी).\n"
            "- Code & Tech Terms: Keep code blocks in standard English, but explain everything in Devanagari Hindi.\n"
            "- STRICT PROHIBITION: Do NOT reply in English unless explicitly asked.\n"
            "- MANDATORY SUGGESTIONS: The 3 to 5 follow-up suggestions at the very end MUST ALSO be in Devanagari Hindi.\n"
            "======================================================================"
        )

    if lang_type == "regional":
        return (
            f"======================================================================\n"
            f"CRITICAL MANDATORY DIRECTIVE: RESPOND IN {label.upper()}\n"
            f"The user asked their question in {label}.\n"
            f"You MUST formulate your ENTIRE response in natural, fluent {label} using its native script.\n"
            f"- STRICT PROHIBITION: Do NOT reply in English unless explicitly asked.\n"
            f"- MANDATORY SUGGESTIONS: The 3 to 5 follow-up suggestions at the very end MUST ALSO be in {label}.\n"
            f"======================================================================"
        )

    return (
        "======================================================================\n"
        "LANGUAGE DIRECTIVE: ENGLISH\n"
        "Respond in natural, fluent, professional English.\n"
        "- MANDATORY SUGGESTIONS: The 3 to 5 follow-up suggestions at the very end MUST be in English.\n"
        "======================================================================"
    )