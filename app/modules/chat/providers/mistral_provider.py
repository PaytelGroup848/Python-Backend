import os

from app.shared.http.http_client import (
    http_client
)

from app.modules.chat.providers.base_provider import (
    BaseProvider
)


class MistralProvider(
    BaseProvider
):

    async def generate(

        self,

        messages,
    ):

        response = await http_client.post(

            "https://api.mistral.ai/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {os.getenv('MISTRAL_API_KEY')}",

                "Content-Type":
                "application/json",
            },

            json={

                "model":
                "mistral-small",

                "messages":
                messages,

                "max_tokens":
                150,
            },
        )

        data = response.json()

        return {

            "model": "mistral",

            "response":
            data["choices"][0]["message"]["content"],

            "usage":
            data.get("usage", {}),
        }