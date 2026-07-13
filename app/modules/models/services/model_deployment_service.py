from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.models.models.model_deployment import (
    ModelDeployment,
)

from app.modules.models.repositories.model_deployment_repository import (
    model_deployment_repository,
)

from app.modules.models.repositories.model_version_repository import (
    model_version_repository,
)

from app.modules.models.schemas.model_deployment_create import (
    ModelDeploymentCreate,
)


class ModelDeploymentService:

    async def create_deployment(
        self,
        db: AsyncSession,
        data: ModelDeploymentCreate,
    ) -> ModelDeployment:

        model_version = await (
            model_version_repository
            .get_by_id(
                db=db,
                model_version_id=(
                    data.model_version_id
                ),
            )
        )

        if model_version is None:

            raise ValueError(
                "Model version not found."
            )

        existing_deployment = await (
            model_deployment_repository
            .get_by_model_version(
                db=db,
                model_version_id=(
                    data.model_version_id
                ),
            )
        )

        if existing_deployment is not None:

            raise ValueError(
                "An active deployment already exists "
                "for this model version."
            )

        deployment = ModelDeployment(

            model_version_id=(
                data.model_version_id
            ),

            deployment_name=(
                data.deployment_name
            ),

            deployment_type=(
                data.deployment_type
            ),

            endpoint_url=(
                data.endpoint_url
            ),

            max_context_window=(
                data.max_context_window
            ),

            gpu_type=(
                data.gpu_type
            ),

            gpu_count=(
                data.gpu_count
            ),

            is_active=True,
        )

        return await (
            model_deployment_repository
            .create(
                db=db,
                deployment=deployment,
            )
        )


    async def get_deployment(
        self,
        db: AsyncSession,
        deployment_id: int,
    ):

        return await (
            model_deployment_repository
            .get_by_id(
                db=db,
                deployment_id=deployment_id,
            )
        )


    async def get_latest_deployment(
        self,
        db: AsyncSession,
        model_version_id: int,
    ):

        return await (
            model_deployment_repository
            .get_latest(
                db=db,
                model_version_id=model_version_id,
            )
        )


    async def list_deployments(
        self,
        db: AsyncSession,
    ):

        return await (
            model_deployment_repository
            .list_all(
                db=db,
            )
        )


    async def list_active_deployments(
        self,
        db: AsyncSession,
    ):

        return await (
            model_deployment_repository
            .list_active(
                db=db,
            )
        )


    async def activate_deployment(
        self,
        db: AsyncSession,
        deployment_id: int,
    ) -> ModelDeployment:

        deployment = await (
            model_deployment_repository
            .get_by_id(
                db=db,
                deployment_id=deployment_id,
            )
        )

        if deployment is None:

            raise ValueError(
                "Deployment not found."
            )

        if deployment.is_active:

            return deployment

        deployment.is_active = True

        return await (
            model_deployment_repository
            .update(
                db=db,
                deployment=deployment,
            )
        )


    async def deactivate_deployment(
        self,
        db: AsyncSession,
        deployment_id: int,
    ) -> ModelDeployment:

        deployment = await (
            model_deployment_repository
            .get_by_id(
                db=db,
                deployment_id=deployment_id,
            )
        )

        if deployment is None:

            raise ValueError(
                "Deployment not found."
            )

        if not deployment.is_active:

            return deployment

        deployment.is_active = False

        return await (
            model_deployment_repository
            .update(
                db=db,
                deployment=deployment,
            )
        )


    async def delete_deployment(
        self,
        db: AsyncSession,
        deployment_id: int,
    ) -> bool:

        deployment = await (
            model_deployment_repository
            .get_by_id(
                db=db,
                deployment_id=deployment_id,
            )
        )

        if deployment is None:

            return False

        await (
            model_deployment_repository
            .delete(
                db=db,
                deployment=deployment,
            )
        )

        return True


model_deployment_service = (
    ModelDeploymentService()
)