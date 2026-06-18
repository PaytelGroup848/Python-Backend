from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.providers.repositories.provider_repository import (
    provider_repository
)


class ProviderService:

    async def get_provider_by_code(
        self,
        db: AsyncSession,
        code: str
    ):

        return await (
            provider_repository
            .get_by_code(
                db,
                code
            )
        )

    async def get_active_providers(
        self,
        db: AsyncSession
    ):

        return await (
            provider_repository
            .get_active_providers(
                db
            )
        )


provider_service = (
    ProviderService()
)