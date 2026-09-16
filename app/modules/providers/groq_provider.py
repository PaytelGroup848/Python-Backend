import os

from app.shared.http.http_client import (
    http_client
)

from app.modules.providers.base_provider import (
    BaseProvider
)

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


class GroqProvider(
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

        safe_messages = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str) and len(content) > 100000:
                content = content[:100000] + "\n...[truncated for length]"
            safe_messages.append({**msg, "content": content})

        response = await http_client.post(

            "https://api.groq.com/openai/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {os.getenv('GROQ_API_KEY')}",

                "Content-Type":
                "application/json",
            },

            json={

                "model": resolved_model,

                "messages": safe_messages,

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

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise Exception("GROQ_API_KEY is not configured")

        safe_messages = []
        for msg in msg_list:
            content = msg.get("content", "")
            if isinstance(content, str) and len(content) > 100000:
                content = content[:100000] + "\n...[truncated for length]"
            safe_messages.append({**msg, "content": content})

        try:
            async with http_client.stream(
                "POST",
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": resolved_model,
                    "messages": safe_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
            ) as response:
                if response.status_code != 200:
                    gen = await self.generate(safe_messages, model=resolved_model, temperature=temperature, max_tokens=max_tokens)
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
            gen = await self.generate(truncated_messages, model=resolved_model, temperature=temperature, max_tokens=max_tokens)
            yield gen["response"]

    async def health_check(
        self
    ):
        return True

