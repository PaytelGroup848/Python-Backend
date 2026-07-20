import tempfile

import edge_tts

# -----------------------------
# ENTERPRISE TTS VOICE
# -----------------------------

VOICE = "en-US-AriaNeural"

# -----------------------------
# TEXT TO SPEECH
# -----------------------------

async def text_to_speech(
    text: str
):

    temp_audio_path = None

    try:

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        )

        temp_audio_path = temp_file.name

        temp_file.close()

        communicate = edge_tts.Communicate(
            text=text,
            voice=VOICE
        )

        await communicate.save(
            temp_audio_path
        )

        return temp_audio_path

    except Exception as e:

        print(f"TTS Error: {e}")

        return None