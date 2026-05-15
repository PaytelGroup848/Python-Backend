from deep_translator import GoogleTranslator


def translate_large_text(
    text: str,
    target_language: str
):
    
    MAX_CHARS = 4000

    chunks = []

    start = 0

    while start < len(text):

        end = start + MAX_CHARS

        chunks.append(text[start:end])

        start = end

    translated_chunks = []

    for chunk in chunks:

        translated = GoogleTranslator(
            source="auto",
            target=target_language
        ).translate(chunk)

        translated_chunks.append(translated)

    return "\n".join(translated_chunks)
    