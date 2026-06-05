import os

from app.shared.http.http_client import (
    http_client
)

from app.modules.chat.providers.base_provider import (
    BaseProvider
)

MODEL_NAME = (
    "llama-3.1-8b-instant"
)


class GroqProvider(
    BaseProvider
):

    async def generate(

        self,

        messages,
    ):

        response = await http_client.post(

            "https://api.groq.com/openai/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {os.getenv('GROQ_API_KEY')}",

                "Content-Type":
                "application/json",
            },

            json={

                "model": MODEL_NAME,

                "messages":
                messages,

                "max_tokens":
                150,
            },
        )

        
        data = response.json()

        print(
            "GROQ RESPONSE:",
            data
        )

        print(
            "GROQ USAGE:",
            data.get(
                "usage",
                {}
            )
        )

        if "choices" not in data:

            raise Exception(
                f"Groq API Error: {data}"
            )

        return {

            "model": MODEL_NAME,

            "response":
            data["choices"][0]["message"]["content"],

            "usage":
            data.get(
                "usage",
                {}
            ),
        }

