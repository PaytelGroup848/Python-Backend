from google import genai

from app.core.config import settings

MODEL_NAME = (
    "gemini-2.5-flash"
)


class GeminiProvider:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    async def generate(
        self,
        messages
    ):

        prompt = messages[-1]["content"]

        response = self.client.models.generate_content(

            model=MODEL_NAME,

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
            MODEL_NAME,

            "response":
            response.text,

            "usage":
            usage
        }