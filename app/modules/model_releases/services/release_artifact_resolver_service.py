from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.model_releases.models.model_release import (
    ModelRelease
)

from app.modules.model_artifacts.models.model_artifact import (
    ModelArtifact
)

from app.modules.model_promotions.repositories.model_promotion_repository import (
    model_promotion_repository
)

from app.modules.evaluations.repositories.evaluation_job_repository import (
    evaluation_job_repository
)

from app.modules.model_artifacts.repositories.model_artifact_repository import (
    model_artifact_repository
)


class ReleaseArtifactResolverService:

    async def resolve(

        self,

        db: AsyncSession,

        release: ModelRelease

    ) -> ModelArtifact:

        promotion = await (
            model_promotion_repository
            .get_by_id(
                db=db,
                promotion_id=release.promotion_id
            )
        )

        if promotion is None:

            raise ValueError(
                "Model promotion not found for release"
            )

        evaluation_job = await (
            evaluation_job_repository
            .get_by_id(
                db=db,
                evaluation_job_id=(
                    promotion.evaluation_job_id
                )
            )
        )

        if evaluation_job is None:

            raise ValueError(
                "Evaluation job not found for promotion"
            )

        artifact = await (
            model_artifact_repository
            .get_by_id(
                db=db,
                artifact_id=(
                    evaluation_job.artifact_id
                )
            )
        )

        if artifact is None:

            raise ValueError(
                "Model artifact not found for evaluation job"
            )

        return artifact


release_artifact_resolver_service = (
    ReleaseArtifactResolverService()
)