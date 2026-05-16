import os
import tempfile

from faster_whisper import WhisperModel

# -----------------------------
# ENTERPRISE WHISPER MODEL
# -----------------------------

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

# -----------------------------
# SPEECH TO TEXT
# -----------------------------

async def speech_to_text(
    audio_bytes: bytes
):

    temp_audio_path = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_audio:

            temp_audio.write(audio_bytes)

            temp_audio_path = temp_audio.name

        segments, _ = model.transcribe(
            temp_audio_path
        )

        full_text = " ".join([
            segment.text
            for segment in segments
        ])

        return full_text

    finally:

        if (
            temp_audio_path
            and os.path.exists(temp_audio_path)
        ):

            os.remove(temp_audio_path)