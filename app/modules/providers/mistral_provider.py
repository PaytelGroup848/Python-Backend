import os

from app.shared.http.http_client import (
    http_client
)

from app.modules.providers.base_provider import (
    BaseProvider
)

MODEL_NAME = (
    "mistral-tiny"
)


class MistralProvider(
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

        metadata: dict | None = None
    ):

        resolved_model = model or MODEL_NAME

        response = await http_client.post(

            "https://api.mistral.ai/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {os.getenv('MISTRAL_API_KEY')}",

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
                f"Mistral API Error: {data}"
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
        messages: list | str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        import json
        resolved_model = model or MODEL_NAME
        msg_list = messages if isinstance(messages, list) else [{"role": "user", "content": str(messages)}]

        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise Exception("MISTRAL_API_KEY is not configured")

        try:
            async with http_client.stream(
                "POST",
                "https://api.mistral.ai/v1/chat/completions",
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
        except Exception:
            gen = await self.generate(msg_list, model=resolved_model, temperature=temperature, max_tokens=max_tokens)
            yield gen["response"]

    async def health_check(
        self
    ):
        return True