import time


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

    def is_available(
        self,
        provider: str,
    ) -> bool:

        provider_data = (
            self.providers[provider]
        )

        now = time.time()

        if (
            provider_data[
                "cooldown_until"
            ] > now
        ):

            return False

        return True

    def record_success(

        self,

        provider: str,

        latency_ms: float,
    ) -> None:

        provider_data = (
            self.providers[provider]
        )

        provider_data[
            "healthy"
        ] = True

        provider_data[
            "failures"
        ] = 0

        provider_data[
            "latency_ms"
        ] = latency_ms

    def record_failure(
        self,
        provider: str,
    ) -> None:

        provider_data = (
            self.providers[provider]
        )

        provider_data[
            "failures"
        ] += 1

        if (
            provider_data[
                "failures"
            ] >= 3
        ):

            provider_data[
                "healthy"
            ] = False

            provider_data[
                "cooldown_until"
            ] = (
                time.time() + 60
            )

    def get_best_provider(
        self,
        providers: list,
    ) -> str | None:

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

            return None

        available.sort(
            key=lambda x: x[1]
        )

        return available[0][0]


provider_health_service = (
    ProviderHealthService()
)