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

        model: str,

        messages: list,

        temperature: float = 0.7,

        max_tokens: int = 4096,

        stream: bool = False,

        tools: list | None = None,

        metadata: dict | None = None
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

                "model": model,

                "messages": messages,

                "temperature": temperature,

                "max_tokens": max_tokens,
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

            "model": model,

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

