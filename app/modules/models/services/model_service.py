from app.models.model import (
    ModelRegistry
)

from app.modules.models.repositories.model_repository import (
    ModelRepository
)


class ModelService:

    def __init__(self):

        self.repository = (
            ModelRepository()
        )

    async def create_model(
        self,
        db,
        model_name: str,
        provider: str,
        description: str | None
    ):

        model = ModelRegistry(

            model_name=model_name,

            provider=provider,

            description=description
        )

        return await (
            self.repository.create(
                db,
                model
            )
        )

    async def get_models(
        self,
        db
    ):

        models = await (
            self.repository
            .get_models(db)
        )

        return {
            "models": models
        }

    async def get_active_models(
        self,
        db
    ):

        return await (
            self.repository
            .get_active_models(db)
        )

    async def get_model(
        self,
        db,
        model_name: str
    ):

        return await (
            self.repository
            .get_by_name(
                db,
                model_name
            )
        )

    async def update_model(
        self,
        db,
        model_name: str,
        payload
    ):

        model = await (
            self.repository
            .get_by_name(
                db,
                model_name
            )
        )

        if not model:

            return None

        if payload.provider is not None:

            model.provider = (
                payload.provider
            )

        if payload.description is not None:

            model.description = (
                payload.description
            )

        if payload.is_active is not None:

            model.is_active = (
                payload.is_active
            )

        return await (
            self.repository.update(
                db,
                model
            )
        )

    async def delete_model(
        self,
        db,
        model_name: str
    ):

        model = await (
            self.repository
            .get_by_name(
                db,
                model_name
            )
        )

        if not model:

            return False

        await (
            self.repository.delete(
                db,
                model
            )
        )

        return True


model_service = (
    ModelService()
)