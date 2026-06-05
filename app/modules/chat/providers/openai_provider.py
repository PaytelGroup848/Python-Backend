import os

from app.shared.http.http_client import (
    http_client
)

from app.modules.chat.providers.base_provider import (
    BaseProvider
)

MODEL_NAME = (
    "gpt-4o-mini"
)


class OpenAIProvider(
    BaseProvider
):

    async def generate(

        self,

        messages,
    ):

        response = await http_client.post(

            "https://api.openai.com/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {os.getenv('OPENAI_API_KEY')}",

                "Content-Type":
                "application/json",
            },

            json={

                "model":
                MODEL_NAME,

                "messages":
                messages,

                "max_tokens":
                150,
            },
        )

        data = response.json()

        if "choices" not in data:

            raise Exception(
                f"OpenAI API Error: {data}"
            )

        return {

            "model":
            MODEL_NAME,

            "response":
            data["choices"][0]["message"]["content"],

            "usage":
            data.get(
                "usage",
                {}
            ),
        }