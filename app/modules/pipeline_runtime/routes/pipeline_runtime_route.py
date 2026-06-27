from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.pipeline_runtime.services.pipeline_runtime_service import (
    pipeline_runtime_service
)

from app.modules.pipeline_runtime.services.pipeline_run_service import (
    pipeline_run_service
)

from app.modules.pipeline_runtime.services.pipeline_step_runtime_service import (
    pipeline_step_runtime_service
)

from app.modules.pipeline_runtime.schemas.pipeline_run_create import (
    PipelineRunCreate
)


router = APIRouter(
    prefix="/pipeline-runtime",
    tags=["Pipeline Runtime"]
)


@router.post("/execute")
async def execute_pipeline(
    payload: PipelineRunCreate,
    db: AsyncSession = Depends(get_db)
):

    try:

        return await (
            pipeline_runtime_service
            .execute_pipeline(
                db=db,
                pipeline_id=payload.pipeline_id,
                dataset_id=payload.dataset_id,
                corpus_source_id=payload.corpus_source_id,
                trigger_type=payload.trigger_type
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/runs/{pipeline_run_id}")
async def get_pipeline_run(
    pipeline_run_id: int,
    db: AsyncSession = Depends(get_db)
):

    pipeline_run = await (
        pipeline_run_service
        .get_by_id(
            db,
            pipeline_run_id
        )
    )

    if not pipeline_run:

        raise HTTPException(
            status_code=404,
            detail="Pipeline run not found."
        )

    return pipeline_run


@router.get("/runs/{pipeline_run_id}/steps")
async def list_pipeline_step_runs(
    pipeline_run_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await (
        pipeline_step_runtime_service
        .list_by_pipeline_run(
            db,
            pipeline_run_id
        )
    )


@router.get("/pipelines/{pipeline_id}/runs")
async def list_pipeline_runs(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await (
        pipeline_run_service
        .list_by_pipeline(
            db,
            pipeline_id
        )
    )