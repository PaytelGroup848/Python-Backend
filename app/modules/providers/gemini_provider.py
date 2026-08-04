from google import genai

from app.core.config import settings

from app.modules.providers.base_provider import (
    BaseProvider
)

MODEL_NAME = (
    "gemini-2.5-flash"
)


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

    async def health_check(
        self
    ):
        return True