import os

from app.shared.http.http_client import (
    http_client
)

from app.modules.providers.base_provider import (
    BaseProvider
)

MODEL_NAME = (
    "mistral-small-latest"
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

    async def health_check(
        self
    ):
        return True