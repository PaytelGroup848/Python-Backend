
import asyncio
import logging
import time

from app.core.config import settings

from app.shared.cache.cache_service import (
    cache_service
)


logger = logging.getLogger(__name__)


class ProviderHealthService:

    def __init__(self):

        self.providers = {
            "groq": {
                "healthy": True,
                "failures": 0,
                "cooldown_until": 0,
                "latency_ms": float("inf"),
            },
            "mistral": {
                "healthy": True,
                "failures": 0,
                "cooldown_until": 0,
                "latency_ms": float("inf"),
            },
            "openai": {
                "healthy": True,
                "failures": 0,
                "cooldown_until": 0,
                "latency_ms": float("inf"),
            },
            "gemini": {
                "healthy": True,
                "failures": 0,
                "cooldown_until": 0,
                "latency_ms": float("inf"),
            },
        }

        self.lock = asyncio.Lock()

    # -----------------------------
    # PERSIST PROVIDER STATE
    # -----------------------------

    async def persist_state(self):

        try:

            await cache_service.set(

                "provider_health_state",

                self.providers.copy(),

                ttl=3600,
            )

        except Exception:

            logger.exception(
                "Failed to persist "
                "provider state"
            )

    # -----------------------------
    # LOAD PROVIDER STATE
    # -----------------------------

    async def load_state(self):

        try:

            cached = await cache_service.get(
                "provider_health_state"
            )

            if cached:

                self.providers = cached

                logger.info(
                    "Provider health "
                    "state restored"
                )

        except Exception:

            logger.exception(
                "Failed to load "
                "provider state"
            )

    # -----------------------------
    # CHECK PROVIDER AVAILABILITY
    # -----------------------------

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

        cooldown_until = (
            provider_data.get(
                "cooldown_until",
                0
            )
        )

        if cooldown_until > now:

            return False

        # auto recover after cooldown

        if not provider_data.get(
            "healthy",
            True
        ):

            provider_data[
                "healthy"
            ] = True

            provider_data[
                "failures"
            ] = 0

            logger.info(
                f"Provider recovered: "
                f"{provider}"
            )

        return True

    # -----------------------------
    # RECORD SUCCESS
    # -----------------------------

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

                logger.warning(
                    f"Unknown provider: "
                    f"{provider}"
                )

                return

            provider_data[
                "healthy"
            ] = True

            provider_data[
                "failures"
            ] = 0

            previous_latency = (
                provider_data.get(
                    "latency_ms",
                    float("inf")
                )
            )

            if (
                previous_latency
                ==
                float("inf")
            ):

                provider_data[
                    "latency_ms"
                ] = latency_ms

            else:

                provider_data[
                    "latency_ms"
                ] = (

                    previous_latency * 0.7
                    +

                    latency_ms * 0.3
                )

    # -----------------------------
    # RECORD FAILURE
    # -----------------------------

    async def record_failure(
        self,
        provider: str,
        is_billing_or_auth: bool = False,
        cooldown_seconds: int | None = None,
    ) -> None:

        async with self.lock:

            provider_data = self.providers.get(provider)

            if not provider_data:
                logger.warning(f"Unknown provider: {provider}")
                return

            provider_data["failures"] += 1
            failures = provider_data["failures"]

            logger.warning(f"Provider failure: {provider} count={failures}")

            if is_billing_or_auth or failures >= settings.PROVIDER_FAILURE_THRESHOLD:
                cooldown = (
                    cooldown_seconds
                    if cooldown_seconds is not None
                    else (1800 if is_billing_or_auth else settings.PROVIDER_COOLDOWN_SECONDS)
                )
                provider_data["healthy"] = False
                provider_data["cooldown_until"] = time.time() + cooldown

                logger.warning(f"Provider cooldown ({cooldown}s): {provider}")
                await self.persist_state()

    # -----------------------------
    # GET RANKED / BEST PROVIDERS
    # -----------------------------

    async def get_ranked_providers(
        self,
        providers: list[str],
    ) -> list[str]:

        async with self.lock:

            available = []

            for provider in providers:
                if self.is_available(provider):
                    latency = self.providers[provider].get("latency_ms", float("inf"))
                    available.append((provider, latency))

            if not available:
                logger.warning("No healthy providers available")
                return []

            available.sort(key=lambda x: x[1])
            return [p for p, _ in available]

    async def get_best_provider(
        self,
        providers: list[str],
    ) -> str | None:

        ranked = await self.get_ranked_providers(providers)
        if not ranked:
            return None

        selected = ranked[0]
        logger.info(f"Selected provider: {selected}")
        return selected

    # -----------------------------
    # PROVIDER STATUS
    # -----------------------------

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

