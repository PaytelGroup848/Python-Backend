from app.modules.admin.repositories.provider_repository import (
    ProviderRepository
)


class ProviderService:

    def __init__(self):

        self.repository = (
            ProviderRepository()
        )

    async def get_providers(self):

        return {
            "providers":
                await self.repository
                .get_provider_status()
        }