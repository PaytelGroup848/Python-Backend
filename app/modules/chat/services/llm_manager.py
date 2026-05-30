import logging
import time

from app.modules.chat.providers.openai_provider import (
    OpenAIProvider
)

from app.modules.chat.providers.groq_provider import (
    GroqProvider
)

from app.modules.chat.services.provider_health import (
    provider_health_service
)
from app.shared.metrics.metrics_service import (
    metrics_service
)

logger = logging.getLogger(__name__)


class LLMManager:

    def __init__(self):

        from app.modules.chat.providers.mistral_provider import (
            MistralProvider
        )

        self.providers = {

            "openai": OpenAIProvider(),

            "groq": GroqProvider(),

            "mistral": MistralProvider(),
        }

    


    async def stream_response(

        self,

        message: str,
    ):
        await metrics_service.increment_requests()

        provider_name = await (
            provider_health_service
            .get_best_provider(
                list(
                    self.providers.keys()
                )
            )
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

        logger.info(
            f"Selected provider: "
            f"{provider_name}"
        )

        start_time = (
            time.perf_counter()
        )

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
                    -
                    start_time
                ) * 1000
            )

            await (
                provider_health_service
                .record_success(
                    provider_name,
                    latency,
                )
            )

        except Exception as e:

            logger.exception(
                f"Provider failed: "
                f"{provider_name}"
            )

            await (
                provider_health_service
                .record_failure(
                    provider_name
                )
            )
            await metrics_service.record_provider_failure(
               provider_name
            )

            fallback_providers = [

                provider

                for provider
                in self.providers.keys()

                if provider != provider_name
            ]

            fallback_provider_name = await (
                provider_health_service
                .get_best_provider(
                    fallback_providers
                )
            )

            await metrics_service.increment_failures()

            if not fallback_provider_name:

                raise e

            logger.warning(
                f"Fallback provider used: "
                f"{fallback_provider_name}"
            )

            fallback_provider = (
                self.providers[
                    fallback_provider_name
                ]
            )

            fallback_start = (
                time.perf_counter()
            )

            async for chunk in (
                fallback_provider.stream_chat(
                    message
                )
            ):

                yield chunk

            fallback_latency = (
                (
                    time.perf_counter()
                    -
                    fallback_start
                ) * 1000
            )

            await (
                provider_health_service
                .record_success(

                    fallback_provider_name,

                    fallback_latency,
                )
            )
            await metrics_service.record_provider_latency(

               provider_name,

               latency,
            )

    async def generate_response(

        self,

        prompt: str,

        user_id: int = 0,

        temperature: float = 0.3,

        stream: bool = False,
    ):

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        provider_name = await (
            provider_health_service
            .get_best_provider(
                list(
                    self.providers.keys()
                )
            )
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

        try:


            result = await provider.generate(
                messages
            )

            return result


        except Exception as e:


            logger.exception(
                f"Provider failed: {provider_name}"
            )

            await (
                provider_health_service
                .record_failure(
                provider_name
            )
        )

            fallback_providers = [

                p

                for p in self.providers.keys()

                if p != provider_name
            ]

            fallback_provider_name = await (
                provider_health_service
                .get_best_provider(
                    fallback_providers
                )
            )

            if not fallback_provider_name:

               raise e

            logger.warning(
                f"Fallback provider used: "
                f"{fallback_provider_name}"
            )

            fallback_provider = (
                self.providers[
                    fallback_provider_name
                ]
            )

            result = await (
                fallback_provider.generate(
                    messages
                )
            )

            return result




llm_manager = (
    LLMManager()
)