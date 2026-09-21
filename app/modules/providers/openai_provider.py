import json
import logging
import os
from typing import AsyncGenerator, Union

from app.core.config import settings
from app.shared.http.http_client import (
    http_client
)

from app.modules.providers.base_provider import (
    BaseProvider
)

logger = logging.getLogger(__name__)

MODEL_NAME = (
    "gpt-4o-mini"
)


class OpenAIProvider(
    BaseProvider
):

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
        api_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")

        response = await http_client.post(

            "https://api.openai.com/v1/chat/completions",

            headers={
                "Authorization":
                f"Bearer {api_key}",

                "Content-Type":
                "application/json",
            },

            json={

                "model": resolved_model,

                "messages": messages,

                "temperature": temperature,

                "max_tokens": max_tokens,
            },
        )

        data = response.json()

        if "choices" not in data:

            raise Exception(
                f"OpenAI API Error: {data}"
            )

        return {

            "model": resolved_model,

            "response":
            data["choices"][0]["message"]["content"],

            "usage":
            data.get(
                "usage",
                {}
            ),
        }

    async def stream_chat(
        self,
        messages: Union[list, str],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        resolved_model = model or MODEL_NAME
        msg_list = messages if isinstance(messages, list) else [{"role": "user", "content": str(messages)}]

        api_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY is not configured")

        try:
            async with http_client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": resolved_model,
                    "messages": msg_list,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
            ) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    logger.error(f"OpenAI stream error {response.status_code}: {err_body.decode('utf-8', errors='ignore')}")
                    gen = await self.generate(msg_list, model=resolved_model, temperature=temperature, max_tokens=max_tokens)
                    yield gen["response"]
                    return

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    line_str = line.strip()
                    if line_str.startswith("data: "):
                        data_part = line_str[6:].strip()
                        if data_part == "[DONE]":
                            break
                        try:
                            chunk_json = json.loads(data_part)
                            delta = chunk_json.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue
        except Exception as exc:
            logger.warning(f"OpenAI streaming fallback: {exc}")
            gen = await self.generate(msg_list, model=resolved_model, temperature=temperature, max_tokens=max_tokens)
            yield gen["response"]

    async def health_check(
        self
    ):
        return True