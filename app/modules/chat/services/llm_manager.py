from app.modules.chat.providers.openai_provider import (
    OpenAIProvider
)

from app.modules.chat.providers.groq_provider import (
    GroqProvider
)

import time

from app.modules.chat.services.provider_health import (
    provider_health_service
)


class LLMManager:

    def __init__(self):

        self.providers = {

            "openai": OpenAIProvider(),

            "groq": GroqProvider(),
        }

        self.default_provider = (
            "groq"
        )

    async def stream_response(

        self,

        message: str,
    ):

        provider_name = (
            provider_health_service
            .get_best_provider()
        )

        if not provider_name:

            raise Exception(
                "No healthy providers available"
            )

        provider = (
            self.providers[
                provider_name
            ]
        )

        start_time = time.perf_counter()

        try:

            async for chunk in (
                provider.stream_chat(
                    message
                )
            ):

                yield chunk

            latency = (
                (
                    time.perf_counter()
                    - start_time
                ) * 1000
            )

            provider_health_service.record_success(

                provider_name,

                latency,
            )

        except Exception:

            provider_health_service.record_failure(
                provider_name
            )

            raise

            yield chunk


llm_manager = (
    LLMManager()
)