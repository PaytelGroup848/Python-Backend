import asyncio

from app.shared.metrics.prometheus_metrics import (
    TOTAL_REQUESTS,
    FAILED_REQUESTS,
    PROVIDER_FAILURES,
    PROVIDER_LATENCY,
    ACTIVE_WEBSOCKETS
)


class MetricsService:

    def __init__(self):

        self.metrics = {

            "total_requests": 0,

            "failed_requests": 0,

            "provider_failures": {},

            "provider_latency": {},

            "active_websockets": 0,

            "embedding_jobs_processed": 0,
        }

        self.lock = asyncio.Lock()

    async def increment_requests(self):

        async with self.lock:

            self.metrics[
                "total_requests"
            ] += 1

            TOTAL_REQUESTS.inc()

    async def increment_failures(self):

        async with self.lock:

            self.metrics[
                "failed_requests"
            ] += 1

            FAILED_REQUESTS.inc()

    async def set_active_websockets(
        self,
        count: int,
    ):

        async with self.lock:

            self.metrics[
                "active_websockets"
            ] = count

            ACTIVE_WEBSOCKETS.set(
                count
            )

    async def record_provider_failure(
        self,
        provider: str,
    ):

        async with self.lock:

            current = (
                self.metrics[
                    "provider_failures"
                ].get(provider, 0)
            )

            self.metrics[
                "provider_failures"
            ][provider] = current + 1

            PROVIDER_FAILURES.labels(
                provider=provider
            ).inc()

    async def record_provider_latency(
        self,
        provider: str,
        latency: float,
    ):

        async with self.lock:

            self.metrics[
                "provider_latency"
            ][provider] = latency

            PROVIDER_LATENCY.labels(
                provider=provider
            ).observe(latency)

    async def increment_embedding_jobs(self):

        async with self.lock:

            self.metrics[
                "embedding_jobs_processed"
            ] += 1

    async def get_metrics(self):

        async with self.lock:

            return self.metrics.copy()


metrics_service = MetricsService()