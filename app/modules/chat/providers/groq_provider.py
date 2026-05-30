import os

from app.shared.http.http_client import (
    http_client
)

from app.modules.chat.providers.base_provider import (
    BaseProvider
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

                "model":
                "llama-3.1-8b-instant",

                "messages":
                messages,

                "max_tokens":
                150,
            },
        )

        
        data = response.json()

        if "choices" not in data:

            raise Exception(
                f"Groq API Error: {data}"
            )

        return {

            "model": "llama",

            "response":
            data["choices"][0]["message"]["content"],

            "usage":
            data.get("usage", {}),
        }

