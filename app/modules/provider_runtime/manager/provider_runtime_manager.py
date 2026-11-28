from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Union

from app.db.database import AsyncSessionLocal
from app.modules.providers.gemini_provider import GeminiProvider
from app.modules.providers.groq_provider import GroqProvider
from app.modules.providers.mistral_provider import MistralProvider
from app.modules.providers.openai_provider import OpenAIProvider
from app.modules.providers.provider_health import provider_health_service
from app.modules.usage.services.usage_tracker import usage_tracker
from app.shared.metrics.metrics_service import metrics_service

logger = logging.getLogger(__name__)

_BILLING_OR_AUTH_MARKERS = (
    "401",
    "402",
    "credit_balance_exhausted",
    "insufficient_quota",
    "billing_no_api_budget_configured",
    "invalid_api_key",
    "payment required",
    "unauthorized",
)


def _is_billing_or_auth_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(marker in msg for marker in _BILLING_OR_AUTH_MARKERS)


async def _track_usage(
    user_id: int,
    provider_name: str,
    result: Dict[str, Any],
    latency_ms: int,
) -> None:
    usage = result.get("usage", {}) or {}
    async with AsyncSessionLocal() as db:
        await usage_tracker.track(
            db=db,
            user_id=user_id,
            api_key_id=None,
            model_name=result.get("model", "unknown"),
            provider=provider_name,
            source="chat",
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_ms=latency_ms,
        )
    logger.info(f"USAGE TRACKED ({provider_name}): {usage}")


class ProviderRuntimeManager:
    """Orchestrates multi-provider LLM streaming and batch execution with full fallback cascade."""

    def __init__(self) -> None:
        self.providers = {
            "openai": OpenAIProvider(),
            "mistral": MistralProvider(),
            "groq": GroqProvider(),
            "gemini": GeminiProvider(),
        }

    async def stream_response(
        self,
        message: Union[str, list],
        temperature: float = 0.65,
        model: str | None = None,
    ):
        await metrics_service.increment_requests()

        candidates = await provider_health_service.get_ranked_providers(list(self.providers.keys()))
        if not candidates:
            raise RuntimeError("No healthy providers available")

        last_err: Exception | None = None
        for idx, provider_name in enumerate(candidates):
            provider = self.providers[provider_name]
            logger.info(f"Selected provider ({'primary' if idx == 0 else f'fallback #{idx}'}): {provider_name}")

            start_time = time.perf_counter()
            yielded_any = False
            try:
                async for chunk in provider.stream_chat(message, model=model, temperature=temperature):
                    yielded_any = True
                    yield chunk

                latency_ms = (time.perf_counter() - start_time) * 1000
                await provider_health_service.record_success(provider_name, latency_ms)
                await metrics_service.record_provider_latency(provider_name, latency_ms)
                return
            except Exception as exc:
                last_err = exc
                failed_ms = (time.perf_counter() - start_time) * 1000
                is_billing = _is_billing_or_auth_error(exc)
                logger.warning(f"Provider {provider_name} failed (billing/auth={is_billing}): {exc}")
                await provider_health_service.record_failure(provider_name, is_billing_or_auth=is_billing)
                await metrics_service.record_provider_failure(provider_name)
                await metrics_service.record_provider_latency(provider_name, failed_ms)

                if yielded_any:
                    await metrics_service.increment_failures()
                    raise

        await metrics_service.increment_failures()
        raise RuntimeError("All AI providers are currently unavailable. Please try again shortly.") from last_err

    async def generate_response(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        user_id: int = 0,
        temperature: float = 0.3,
        stream: bool = False,
    ) -> Dict[str, Any]:
        messages = (
            prompt
            if isinstance(prompt, list)
            else [{"role": "user", "content": str(prompt)}]
        )

        candidates = await provider_health_service.get_ranked_providers(list(self.providers.keys()))
        if not candidates:
            raise RuntimeError("No healthy providers available")

        last_err: Exception | None = None
        for idx, provider_name in enumerate(candidates):
            provider = self.providers[provider_name]
            logger.info(f"Batch selected provider ({'primary' if idx == 0 else f'fallback #{idx}'}): {provider_name}")

            start_time = time.perf_counter()
            try:
                result = await provider.generate(messages=messages, temperature=temperature)
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                await provider_health_service.record_success(provider_name, float(latency_ms))
                await _track_usage(user_id, provider_name, result, latency_ms)
                return result
            except Exception as exc:
                last_err = exc
                is_billing = _is_billing_or_auth_error(exc)
                logger.warning(f"Batch provider {provider_name} failed (billing/auth={is_billing}): {exc}")
                await provider_health_service.record_failure(provider_name, is_billing_or_auth=is_billing)

        raise RuntimeError("All AI providers are currently unavailable. Please try again shortly.") from last_err


provider_runtime_manager = ProviderRuntimeManager()
