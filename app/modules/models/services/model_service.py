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
        code: str,
        display_name: str,
        provider_id: int,
        description: str | None
    ):

        model = ModelRegistry(

            code=code,

            display_name=display_name,

            provider_id=provider_id,

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
        code: str
    ):

        return await (
            self.repository.get_by_code(
                db,
                code
            )
        )

    async def update_model(
        self,
        db,
        code: str,
        payload
    ):

        model = await (
            self.repository.get_by_code(
                db,
                code
            )
        )

        if not model:

            return None

        if payload.provider_id is not None:

            model.provider_id = (
                payload.provider_id
            )

        if payload.display_name is not None:

            model.display_name = (
                payload.display_name
            )

        if payload.status is not None:

            model.status = (
                payload.status
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
        code: str
    ):

        model = await (
            self.repository.get_by_code(
                db,
                code
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
    
    async def get_models_by_status(
        self,
        db,
        status: str
    ):

        return await self.repository.get_by_status(
            db,
            status
        )
    
    async def get_models_by_provider(
        self,
        db,
        provider_id: int
    ):

        return await self.repository.get_by_provider(
            db,
            provider_id
        )


model_service = (
    ModelService()
)