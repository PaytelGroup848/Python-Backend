from google import genai

from app.core.config import settings

from app.modules.providers.base_provider import (
    BaseProvider
)

import os

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


class GeminiProvider(
    BaseProvider
):

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    async def generate(
        self,
        messages: list,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        tools: list | None = None,
        metadata: dict | None = None,
    ):

        resolved_model = model or MODEL_NAME

        prompt = messages[-1]["content"]

        response = self.client.models.generate_content(

            model=resolved_model,

            contents=prompt
        )

        usage = {}

        try:

            usage = {

                "prompt_tokens":
                response.usage_metadata.prompt_token_count,

                "completion_tokens":
                response.usage_metadata.candidates_token_count,

                "total_tokens":
                response.usage_metadata.total_token_count
            }

        except Exception:

            usage = {}

        return {

            "model":
            resolved_model,

            "response":
            response.text,

            "usage":
            usage
        }

    async def stream_chat(
        self,
        messages: list | str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        resolved_model = model or MODEL_NAME
        prompt = messages[-1]["content"] if isinstance(messages, list) and messages else str(messages)

        try:
            stream = self.client.models.generate_content_stream(
                model=resolved_model,
                contents=prompt
            )
            for chunk in stream:
                text_part = chunk.text
                if text_part:
                    yield text_part
        except Exception:
            msg_list = messages if isinstance(messages, list) else [{"role": "user", "content": str(messages)}]
            gen = await self.generate(msg_list, model=resolved_model, temperature=temperature, max_tokens=max_tokens)
            yield gen["response"]

    async def health_check(
        self
    ):
        return True