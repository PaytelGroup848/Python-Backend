import asyncio
import logging
import time

from app.core.config import (
    PROVIDER_FAILURE_THRESHOLD,
    PROVIDER_COOLDOWN_SECONDS
)
from app.shared.cache.cache_service import (
    cache_service
)

logger = logging.getLogger(__name__)


class ProviderHealthService:

    def __init__(self):

        self.providers = {

            "openai": {

                "healthy": True,

                "failures": 0,

                "cooldown_until": 0,

                "latency_ms": 0,
            },

            "mistral": {

                "healthy": True,

                "failures": 0,

                "cooldown_until": 0,

                "latency_ms": 0,
            },

            "llama": {

                "healthy": True,

                "failures": 0,

                "cooldown_until": 0,

                "latency_ms": 0,
            },
        }

        self.lock = asyncio.Lock()
        async def persist_state(self):

            await cache_service.set(

                "provider_health_state",

                self.providers,

                ttl=3600,
            )

    def is_available(
        self,
        provider: str,
    ) -> bool:

        provider_data = (
            self.providers.get(provider)
        )

        if not provider_data:

            return False

        now = time.time()

        if (
            provider_data[
                "cooldown_until"
            ] > now
        ):

            return False

        if not provider_data["healthy"]:

            provider_data[
                "healthy"
            ] = True

            provider_data[
                "failures"
            ] = 0

        return True

    async def record_success(

        self,

        provider: str,

        latency_ms: float,
    ) -> None:

        async with self.lock:

            provider_data = (
                self.providers.get(provider)
            )

            if not provider_data:

                return

            provider_data[
                "healthy"
            ] = True

            provider_data[
                "failures"
            ] = 0

            previous_latency = (
                provider_data[
                    "latency_ms"
                ]
            )

            if previous_latency == 0:

                provider_data[
                    "latency_ms"
                ] = latency_ms

                await self.persist_state()

            else:

                provider_data[
                    "latency_ms"
                ] = (

                    previous_latency * 0.7
                    +

                    latency_ms * 0.3
                )

                await self.persist_state()

    async def record_failure(
        self,
        provider: str,
    ) -> None:

        async with self.lock:

            provider_data = (
                self.providers.get(provider)
            )

            if not provider_data:

                return

            provider_data[
                "failures"
            ] += 1

            if (
                provider_data[
                    "failures"
                ]
                >=
                PROVIDER_FAILURE_THRESHOLD
            ):

                provider_data[
                    "healthy"
                ] = False

                provider_data[
                    "cooldown_until"
                ] = (
                    time.time()
                    +
                    PROVIDER_COOLDOWN_SECONDS
                )

                logger.warning(
                    f"Provider cooldown: "
                    f"{provider}"
                )

                await self.persist_state()

    async def get_best_provider(
        self,
        providers: list,
    ) -> str | None:

        async with self.lock:

            available = []

            for provider in providers:

                if self.is_available(
                    provider
                ):

                    available.append(
                        (
                            provider,

                            self.providers[
                                provider
                            ][
                                "latency_ms"
                            ],
                        )
                    )

            if not available:

                logger.warning(
                    "No healthy providers available"
                )

                return None

            available.sort(
                key=lambda x: x[1]
            )

            return available[0][0]

    async def get_provider_status(
        self
    ) -> dict:

        async with self.lock:

            return {
                provider: data.copy()
                for provider, data
                in self.providers.items()
            }


provider_health_service = (
    ProviderHealthService()
)