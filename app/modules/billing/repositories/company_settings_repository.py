from sqlalchemy import select



from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.company_settings import (
    CompanySettings
)


class CompanySettingsRepository:

    async def get_active_settings(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(
                CompanySettings
            )

            .where(
                CompanySettings.is_active.is_(True)
            )

            .limit(1)
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_by_id(
        self,
        db: AsyncSession,
        settings_id: int
    ):

        result = await db.execute(

            select(
                CompanySettings
            )

            .where(
                CompanySettings.id == settings_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def create(
        self,
        db: AsyncSession,
        settings: CompanySettings
    ):

        db.add(settings)

        await db.commit()

        await db.refresh(
            settings
        )

        return settings

    async def update(
        self,
        db: AsyncSession,
        settings: CompanySettings
    ):

        await db.commit()

        await db.refresh(
            settings
        )

        return settings


company_settings_repository = (
    CompanySettingsRepository()
)