from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.modules.training.models.training_configuration import (
    TrainingConfiguration,
)


class TrainingConfigurationRepository:

    # --------------------------------------------------
    # Create / Update / Delete
    # --------------------------------------------------

    async def create(
        self,
        db: AsyncSession,
        training_configuration: TrainingConfiguration,
    ):

        db.add(training_configuration)

        await db.flush()

        await db.refresh(training_configuration)

        return training_configuration


    async def update(
        self,
        db: AsyncSession,
        training_configuration: TrainingConfiguration,
    ):

        await db.flush()

        await db.refresh(training_configuration)

        return training_configuration


    async def delete(
        self,
        db: AsyncSession,
        training_configuration: TrainingConfiguration,
    ):

        await db.delete(training_configuration)


    # --------------------------------------------------
    # Single Reads
    # --------------------------------------------------

    async def get_by_id(
        self,
        db: AsyncSession,
        training_configuration_id: int,
    ):

        result = await db.execute(
            select(
                TrainingConfiguration
            ).where(
                TrainingConfiguration.id
                == training_configuration_id
            )
        )

        return result.scalar_one_or_none()


    async def get_by_id_for_update(
        self,
        db: AsyncSession,
        training_configuration_id: int,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.id
                == training_configuration_id
            )
            .with_for_update()

        )

        return result.scalar_one_or_none()


    async def get_by_code_and_version(
        self,
        db: AsyncSession,
        configuration_code: str,
        version: int,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.configuration_code
                == configuration_code
            )
            .where(
                TrainingConfiguration.version
                == version
            )

        )

        return result.scalar_one_or_none()


    async def get_latest_version(
        self,
        db: AsyncSession,
        configuration_code: str,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.configuration_code
                == configuration_code
            )
            .order_by(
                TrainingConfiguration.version.desc()
            )
            .limit(1)

        )

        return result.scalar_one_or_none()
    
    async def get_latest_version_for_update(
        self,
        db: AsyncSession,
        configuration_code: str,
    ):

        result = await db.execute(
 
            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.configuration_code
                ==
                configuration_code
            )
            .order_by(
                TrainingConfiguration.version.desc()
            )
            .limit(1)
            .with_for_update()

        )

        return result.scalar_one_or_none()


    async def get_active_by_code(
        self,
        db: AsyncSession,
        configuration_code: str,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.configuration_code
                == configuration_code
            )
            .where(
                TrainingConfiguration.is_active.is_(True)
            )
            .order_by(
                TrainingConfiguration.version.desc()
            )
            .limit(1)

        )

        return result.scalar_one_or_none()


    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    async def exists_by_code(
        self,
        db: AsyncSession,
        configuration_code: str,
    ) -> bool:

        result = await db.execute(

            select(
                TrainingConfiguration.id
            )
            .where(
                TrainingConfiguration.configuration_code
                == configuration_code
            )
            .limit(1)

        )

        return result.scalar_one_or_none() is not None


    async def exists_by_display_name(
        self,
        db: AsyncSession,
        display_name: str,
    ) -> bool:

        result = await db.execute(

            select(
                TrainingConfiguration.id
            )
            .where(
                TrainingConfiguration.display_name
                == display_name
            )
            .limit(1)

        )

        return result.scalar_one_or_none() is not None


    # --------------------------------------------------
    # Lists
    # --------------------------------------------------

    async def list_all(
        self,
        db: AsyncSession,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .order_by(
                TrainingConfiguration.configuration_code,
                TrainingConfiguration.version.desc(),
            )

        )

        return result.scalars().all()


    async def list_active(
        self,
        db: AsyncSession,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.is_active.is_(True)
            )
            .order_by(
                TrainingConfiguration.configuration_code,
                TrainingConfiguration.version.desc(),
            )

        )

        return result.scalars().all()


    async def list_versions(
        self,
        db: AsyncSession,
        configuration_code: str,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.configuration_code
                == configuration_code
            )
            .order_by(
                TrainingConfiguration.version.desc()
            )

        )

        return result.scalars().all()


    async def list_by_training_type(
        self,
        db: AsyncSession,
        training_type: str,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.training_type
                == training_type
            )
            .order_by(
                TrainingConfiguration.configuration_code,
                TrainingConfiguration.version.desc(),
            )

        )

        return result.scalars().all()


    async def list_by_runtime_code(
        self,
        db: AsyncSession,
        runtime_code: str,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.runtime_code
                == runtime_code
            )
            .order_by(
                TrainingConfiguration.configuration_code,
                TrainingConfiguration.version.desc(),
            )

        )

        return result.scalars().all()


    # --------------------------------------------------
    # Activation
    # --------------------------------------------------

    async def deactivate_code(
        self,
        db: AsyncSession,
        configuration_code: str,
    ):

        result = await db.execute(

            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.configuration_code
                == configuration_code
            )
            .with_for_update()

        )

        rows = result.scalars().all()

        for row in rows:
            row.is_active = False

        await db.flush()

        return rows


    async def activate(
        self,
        db: AsyncSession,
        training_configuration: TrainingConfiguration,
    ):

        training_configuration.is_active = True

        await db.flush()

        await db.refresh(
            training_configuration
        )

        return training_configuration


training_configuration_repository = (
    TrainingConfigurationRepository()
)