from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)


from app.modules.tokenizers.models.tokenizer_implementation import (
    TokenizerImplementation,
)

from app.modules.tokenizers.models.tokenizer_training_configuration import (
    TokenizerTrainingConfiguration,
)

from app.modules.tokenizers.models.tokenizer_training_job import (
    TokenizerTrainingJob,
)

from app.modules.tokenizers.models.tokenizer_version import (
    TokenizerVersion,
)

from app.modules.tokenizers.models.tokenizer_version_artifact import (
    TokenizerVersionArtifact,
)


class TokenizerTrainingLifecycleRepository:

    async def get_job_by_id(
        self,
        db: AsyncSession,
        job_id: int,
        for_update: bool = False,
    ) -> TokenizerTrainingJob | None:

        statement = (
            select(
                TokenizerTrainingJob
            )
            .where(
                TokenizerTrainingJob.id
                ==
                job_id
            )
        )

        if for_update:

            statement = (
                statement.with_for_update()
            )

        result = await db.execute(
            statement
        )

        return result.scalar_one_or_none()


    async def get_training_configuration_by_id(
        self,
        db: AsyncSession,
        configuration_id: int,
    ) -> TokenizerTrainingConfiguration | None:

        result = await db.execute(
            select(
                TokenizerTrainingConfiguration
            )
            .where(
                TokenizerTrainingConfiguration.id
                ==
                configuration_id
            )
        )

        return result.scalar_one_or_none()


    async def get_implementation_by_id(
        self,
        db: AsyncSession,
        implementation_id: int,
    ) -> TokenizerImplementation | None:

        result = await db.execute(
            select(
                TokenizerImplementation
            )
            .where(
                TokenizerImplementation.id
                ==
                implementation_id
            )
        )

        return result.scalar_one_or_none()


    async def create_version(
        self,
        db: AsyncSession,
        version: TokenizerVersion,
    ) -> TokenizerVersion:

        db.add(
            version
        )

        await db.flush()
        await db.refresh(
            version
        )

        return version


    async def create_version_artifact(
        self,
        db: AsyncSession,
        artifact: TokenizerVersionArtifact,
    ) -> TokenizerVersionArtifact:

        db.add(
            artifact
        )

        await db.flush()
        await db.refresh(
            artifact
        )

        return artifact


    async def list_version_artifacts(
        self,
        db: AsyncSession,
        tokenizer_version_id: int,
    ) -> list[
        TokenizerVersionArtifact
    ]:

        result = await db.execute(
            select(
                TokenizerVersionArtifact
            )
            .where(
                TokenizerVersionArtifact.tokenizer_version_id
                ==
                tokenizer_version_id
            )
            .order_by(
                TokenizerVersionArtifact.id.asc()
            )
        )

        return list(
            result.scalars().all()
        )


    async def get_version_by_id(
        self,
        db: AsyncSession,
        tokenizer_version_id: int,
    ) -> TokenizerVersion | None:

        result = await db.execute(
            select(
                TokenizerVersion
            )
            .where(
                TokenizerVersion.id
                ==
                tokenizer_version_id
            )
        )

        return result.scalar_one_or_none()


tokenizer_training_lifecycle_repository = (
    TokenizerTrainingLifecycleRepository()
)