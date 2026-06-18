from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.providers.models.provider import Provider


class ProviderRepository:

    async def get_by_id(
        self,
        db: AsyncSession,
        provider_id: int
    ):

        result = await db.execute(

            select(Provider)

            .where(
                Provider.id == provider_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        db: AsyncSession,
        code: str
    ):

        result = await db.execute(

            select(Provider)

            .where(
                Provider.code == code
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(Provider)
        )

        return result.scalars().all()

    async def get_active_providers(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(Provider)

            .where(
                Provider.is_active == True
            )

            .order_by(
                Provider.priority.asc()
            )
        )

        return result.scalars().all()


provider_repository = (
    ProviderRepository()
)