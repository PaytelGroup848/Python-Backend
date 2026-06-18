from app.modules.billing.models.company_settings import (
    CompanySettings
)

from app.modules.billing.repositories.company_settings_repository import (
    company_settings_repository
)


class CompanySettingsService:

    async def get_company_settings(
        self,
        db
    ):

        return await (
            company_settings_repository
            .get_active_settings(
                db
            )
        )

    async def create_company_settings(
        self,
        db,
        data: dict
    ):

        existing = await (
            company_settings_repository
            .get_active_settings(
                db
            )
        )

        if existing:

            return existing

        settings = CompanySettings(
            **data
        )

        return await (
            company_settings_repository
            .create(
                db,
                settings
            )
        )

    async def update_company_settings(
        self,
        db,
        data: dict
    ):

        settings = await (
            company_settings_repository
            .get_active_settings(
                db
            )
        )

        if not settings:

            settings = CompanySettings()

            for key, value in data.items():

                setattr(
                    settings,
                    key,
                    value
                )

            return await (
                company_settings_repository
                .create(
                    db,
                    settings
                )
            )

        for key, value in data.items():

            setattr(
                settings,
                key,
                value
            )

        return await (
            company_settings_repository
            .update(
                db,
                settings
            )
        )


company_settings_service = (
    CompanySettingsService()
)