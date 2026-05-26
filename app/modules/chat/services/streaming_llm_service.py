from openai import AsyncOpenAI

from app.core.config import settings


client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)


async def stream_llm_response(
    message: str
):

    stream = await client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],

        stream=True,
    )

    async for chunk in stream:

        delta = (
            chunk.choices[0]
            .delta
            .content
        )

        if delta:

            yield delta