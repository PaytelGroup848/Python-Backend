import logging
import os
import re
import tempfile
from typing import AsyncGenerator, Optional

import edge_tts

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# ENTERPRISE NEURAL TTS VOICES (Microsoft Azure High-Fidelity Neural Speech)
# ------------------------------------------------------------------------------
DEFAULT_EN_VOICE = "en-US-JennyNeural"
DEFAULT_HI_VOICE = "hi-IN-SwaraNeural"

# Backward compatibility constant
VOICE = DEFAULT_EN_VOICE


def sanitize_speech_text(text: str) -> str:
    """
    Cleans markdown formatting, code blocks, URLs, and citations
    so the speech synthesizer reads fluent, natural prose.
    """
    if not text or not text.strip():
        return ""

    cleaned = text

    # 1. Remove markdown code fences and their contents
    cleaned = re.sub(r"```[\s\S]*?```", " [code block omitted] ", cleaned)

    # 2. Remove inline code snippets `code`
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)

    # 3. Remove citations like [1], [2], [1, 2]
    cleaned = re.sub(r"\[\d+(?:[,\s]+\d+)*\]", "", cleaned)

    # 4. Convert markdown links [Text](url) -> Text
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)

    # 5. Clean URLs to readable domain names
    cleaned = re.sub(r"https?://(?:www\.)?([^\s/]+)[^\s]*", r"\1 website", cleaned)

    # 6. Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)

    # 7. Remove bold, italic, strikethrough markers (*, **, _, ~)
    cleaned = re.sub(r"[*_~]{1,3}", "", cleaned)

    # 8. Clean markdown headers (# Header -> Header)
    cleaned = re.sub(r"^#{1,6}\s+", "", cleaned, flags=re.MULTILINE)

    # 9. Clean markdown list markers (*, -, +, 1.)
    cleaned = re.sub(r"^\s*[-*+]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\d+\.\s+", "", cleaned, flags=re.MULTILINE)

    # 10. Clean blockquotes (> quote)
    cleaned = re.sub(r"^\s*>\s*", "", cleaned, flags=re.MULTILINE)

    # 11. Normalize excess whitespace and linebreaks
    cleaned = re.sub(r"\n+", " ", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    return cleaned.strip()


def resolve_voice_for_text(text: str, preferred_voice: Optional[str] = None) -> str:
    """
    Resolves the best Microsoft Neural Voice based on user preference or script detection.
    """
    if preferred_voice and preferred_voice.strip():
        return preferred_voice.strip()

    # Detect Devanagari script for Hindi/Marathi
    if re.search(r"[\u0900-\u097F]", text):
        return DEFAULT_HI_VOICE

    return DEFAULT_EN_VOICE


async def stream_neural_speech(
    text: str,
    voice: Optional[str] = None,
    rate: str = "+0%",
    pitch: str = "+0Hz",
) -> AsyncGenerator[bytes, None]:
    """
    Asynchronously yields MP3 audio bytes directly from the edge_tts neural stream.
    Zero disk I/O, ultra-low latency playback.
    """
    clean_text = sanitize_speech_text(text)
    if not clean_text:
        return

    selected_voice = resolve_voice_for_text(clean_text, voice)
    logger.info(f"Streaming TTS audio using voice: {selected_voice} (length: {len(clean_text)} chars)")

    try:
        communicate = edge_tts.Communicate(
            text=clean_text,
            voice=selected_voice,
            rate=rate,
            pitch=pitch,
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    except Exception as e:
        logger.error(f"Neural TTS streaming failed: {e}", exc_info=True)
        return


async def text_to_speech(text: str, voice: Optional[str] = None) -> Optional[str]:
    """
    Legacy helper: synthesizes speech to a local temporary MP3 file and returns its path.
    Preserved for backwards compatibility with existing websocket audio routes.
    """
    temp_audio_path = None
    try:
        clean_text = sanitize_speech_text(text)
        if not clean_text:
            return None

        selected_voice = resolve_voice_for_text(clean_text, voice)

        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_audio_path = temp_file.name
        temp_file.close()

        communicate = edge_tts.Communicate(text=clean_text, voice=selected_voice)
        await communicate.save(temp_audio_path)
        return temp_audio_path

    except Exception as e:
        logger.error(f"TTS Error in text_to_speech: {e}", exc_info=True)
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except OSError:
                pass
        return None
