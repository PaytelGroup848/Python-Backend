from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.data_pipelines.models.data_pipeline import (
    DataPipeline
)

from app.modules.data_pipelines.models.data_pipeline_step import (
    DataPipelineStep
)

from app.modules.data_pipelines.schemas.data_pipeline_create import (
    DataPipelineCreate
)

from app.modules.data_pipelines.schemas.data_pipeline_update import (
    DataPipelineUpdate
)

from app.modules.data_pipelines.schemas.data_pipeline_step_create import (
    DataPipelineStepCreate
)

from app.modules.data_pipelines.schemas.data_pipeline_step_update import (
    DataPipelineStepUpdate
)

from app.modules.data_pipelines.repositories.data_pipeline_repository import (
    data_pipeline_repository
)

from app.modules.data_pipelines.repositories.data_pipeline_step_repository import (
    data_pipeline_step_repository
)

from app.modules.corpora.repositories.corpus_repository import (
    corpus_repository
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository
)
from app.modules.storage_registry.repositories.storage_instance_repository import (
    storage_instance_repository
)

class DataPipelineService:

    async def create_pipeline(
        self,
        db: AsyncSession,
        payload: DataPipelineCreate
    ):
        
        corpus = await (

            corpus_repository
            .get_by_id(
                db,
                payload.corpus_id
            )
        )

        if not corpus:

            raise ValueError(
                "Corpus not found"
            )

        if payload.dataset_id is not None:

            dataset = await (

                dataset_repository
                .get_by_id(
                    db,
                    payload.dataset_id
                )
            )

            if not dataset:

                raise ValueError(
                    "Dataset not found"
                )

        exists = await (

            data_pipeline_repository
            .exists_pipeline_code(
                db,
                payload.pipeline_code
            )
        )

        if exists:

            raise ValueError(
                "Pipeline code already exists"
            )
        

        pipeline = DataPipeline(

            corpus_id=payload.corpus_id,

            name=payload.name,

            pipeline_code=payload.pipeline_code,

            dataset_id=payload.dataset_id,

            status=payload.status
        )

        return await data_pipeline_repository.create(
            db,
            pipeline
        )

    async def get_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        return await data_pipeline_repository.get_by_id(
            db,
            pipeline_id
        )

    async def list_pipelines(
        self,
        db: AsyncSession
    ):

        return await data_pipeline_repository.list_all(
            db
        )

    async def update_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int,
        payload: DataPipelineUpdate
    ):

        pipeline = (
            await data_pipeline_repository.get_by_id(
                db,
                pipeline_id
            )
        )

        if not pipeline:

            raise ValueError(
                "Pipeline not found"
            )
        
        if payload.corpus_id is not None:

            corpus = await (

                corpus_repository
                .get_by_id(
                    db,
                    payload.corpus_id
                )
            )

            if not corpus:

                raise ValueError(
                    "Corpus not found"
                )


        if payload.dataset_id is not None:

            dataset = await (

                dataset_repository
                .get_by_id(
                    db,
                    payload.dataset_id
                )
            )

            if not dataset:

                raise ValueError(
                    "Dataset not found"
                )


        if payload.pipeline_code is not None:

            existing = await (

                data_pipeline_repository
                .get_by_pipeline_code(
                    db,
                    payload.pipeline_code
                )
            )

            if (
                existing
                and
                existing.id != pipeline.id
            ):

                raise ValueError(
                    "Pipeline code already exists"
                )
        

        update_data = (
            payload.model_dump(
                exclude_unset=True
            )
        )

        for field, value in update_data.items():

            setattr(
                pipeline,
                field,
                value
            )

        return await data_pipeline_repository.update(
            db,
            pipeline
        )
    
    async def delete_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        pipeline = (
            await data_pipeline_repository.get_by_id(
                db,
                pipeline_id
            )
        )

        if not pipeline:

            raise ValueError(
                "Pipeline not found"
            )

        await data_pipeline_repository.delete(
            db,
            pipeline
        )

        return {
            "message": "Pipeline deleted"
        }

    async def activate_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        pipeline = (
            await data_pipeline_repository.get_by_id(
                db,
                pipeline_id
            )
        )

        if not pipeline:

            raise ValueError(
                "Pipeline not found"
            )

        pipeline.status = "ACTIVE"

        return await data_pipeline_repository.update(
            db,
            pipeline
        )

    async def deactivate_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        pipeline = (
            await data_pipeline_repository.get_by_id(
                db,
                pipeline_id
            )
        )

        if not pipeline:

            raise ValueError(
                "Pipeline not found"
            )

        pipeline.status = "INACTIVE"

        return await data_pipeline_repository.update(
            db,
            pipeline
        )

    async def add_step(
        self,
        db: AsyncSession,
        payload: DataPipelineStepCreate
    ):

        pipeline = (
            await data_pipeline_repository.get_by_id(
                db,
                payload.pipeline_id
            )
        )

        if not pipeline:

            raise ValueError(
                "Pipeline not found"
            )

        existing_step = (
            await data_pipeline_step_repository.get_by_pipeline_and_order(
                db,
                payload.pipeline_id,
                payload.step_order
            )
        )

        if existing_step:

            raise ValueError(
                "Step order already exists"
            )
        
        existing_step_code = (
            await data_pipeline_step_repository.get_by_pipeline_and_step_code(
                db,
                payload.pipeline_id,
                payload.step_code
            )
        )

        if existing_step_code:

            raise ValueError(
                "Step code already exists"
            )
        
        if payload.output_storage_instance_id is not None:

            storage_instance = await (
                storage_instance_repository
                .get_active_by_id(
                    db=db,
                    storage_instance_id=(
                        payload.output_storage_instance_id
                    ),
                )
            )

            if storage_instance is None:

                raise ValueError(
                    "Active output storage instance not found"
                )

        step = DataPipelineStep(

            pipeline_id=payload.pipeline_id,

            step_order=payload.step_order,

            step_code=payload.step_code,

            step_type=payload.step_type,

            runtime_code=payload.runtime_code,

            output_storage_instance_id=(
                payload.output_storage_instance_id
            ),

            configuration_json=payload.configuration_json,

            status=payload.status
        )

        return await data_pipeline_step_repository.create(
            db,
            step
        )

    async def list_steps(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        return await data_pipeline_step_repository.list_by_pipeline(
            db,
            pipeline_id
        )
    
    async def get_step(
        self,
        db: AsyncSession,
        pipeline_step_id: int
    ):

        return await data_pipeline_step_repository.get_by_id(
            db,
            pipeline_step_id
        )

    async def update_step(
        self,
        db: AsyncSession,
        pipeline_step_id: int,
        payload: DataPipelineStepUpdate
    ):

        step = (
            await data_pipeline_step_repository.get_by_id(
                db,
                pipeline_step_id
            )
        )

        if not step:

            raise ValueError(
                "Pipeline step not found"
            )
        
        existing_order = None
        if payload.step_order is not None:

            existing_order = (
                await data_pipeline_step_repository.get_by_pipeline_and_order(
                    db,
                    step.pipeline_id,
                    payload.step_order
                )
            )

        if (
            existing_order
            and
            existing_order.id != step.id
        ):

            raise ValueError(
                "Step order already exists"
            )
        
        
        existing_code = None
        if payload.step_code:

            existing_code = (
                await data_pipeline_step_repository.get_by_pipeline_and_step_code(
                    db,
                    step.pipeline_id,
                    payload.step_code
                )
            )

        if (
            existing_code
            and
            existing_code.id != step.id
        ):

            raise ValueError(
                "Step code already exists"
            )
        
        if (
            "output_storage_instance_id"
            in payload.model_fields_set
            and
            payload.output_storage_instance_id
            is not None
        ):

            storage_instance = await (
                storage_instance_repository
                .get_active_by_id(
                    db=db,
                    storage_instance_id=(
                        payload.output_storage_instance_id
                    ),
                )
            )

            if storage_instance is None:

                raise ValueError(
                    "Active output storage instance not found"
                )

        update_data = (
            payload.model_dump(
                exclude_unset=True
            )
        )

        for field, value in update_data.items():

            setattr(
                step,
                field,
                value
            )

        return await data_pipeline_step_repository.update(
            db,
            step
        )

    async def delete_step(
        self,
        db: AsyncSession,
        pipeline_step_id: int
    ):

        step = (
            await data_pipeline_step_repository.get_by_id(
                db,
                pipeline_step_id
            )
        )

        if not step:

            raise ValueError(
                "Pipeline step not found"
            )

        await data_pipeline_step_repository.delete(
            db,
            step
        )

        return {
            "message": "Pipeline step deleted"
        }


data_pipeline_service = (
    DataPipelineService()
)