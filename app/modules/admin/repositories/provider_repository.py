class ProviderRepository:

    async def get_provider_status(self):

        return [
            {
                "name": "OpenAI",
                "status": "healthy",
                "latency_ms": 220,
            },
            {
                "name": "Groq",
                "status": "healthy",
                "latency_ms": 95,
            },
            {
                "name": "Mistral",
                "status": "healthy",
                "latency_ms": 140,
            },
        ]