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

from app.modules.data_pipelines.services.data_pipeline_service import (
    data_pipeline_service
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


router = APIRouter(
    prefix="/data-pipelines",
    tags=["Data Pipelines"]
)


@router.post("/")
async def create_pipeline(
    payload: DataPipelineCreate,
    db: AsyncSession = Depends(get_db)
):

    try:

        return await data_pipeline_service.create_pipeline(
            db,
            payload
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/")
async def list_pipelines(
    db: AsyncSession = Depends(get_db)
):

    return await data_pipeline_service.list_pipelines(
        db
    )


@router.get("/steps/{step_id}")
async def get_step(
    step_id: int,
    db: AsyncSession = Depends(get_db)
):

    step = await data_pipeline_service.get_step(
        db,
        step_id
    )

    if not step:

        raise HTTPException(
            status_code=404,
            detail="Pipeline step not found"
        )

    return step


@router.patch("/steps/{step_id}")
async def update_step(
    step_id: int,
    payload: DataPipelineStepUpdate,
    db: AsyncSession = Depends(get_db)
):

    try:

        return await data_pipeline_service.update_step(
            db,
            step_id,
            payload
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/steps/{step_id}")
async def delete_step(
    step_id: int,
    db: AsyncSession = Depends(get_db)
):

    try:

        return await data_pipeline_service.delete_step(
            db,
            step_id
        )

    except ValueError as e:
   
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    

@router.get("/{pipeline_id}")
async def get_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):

    pipeline = await data_pipeline_service.get_pipeline(
        db,
        pipeline_id
    )

    if not pipeline:

        raise HTTPException(
            status_code=404,
            detail="Pipeline not found"
        )

    return pipeline


@router.patch("/{pipeline_id}")
async def update_pipeline(
    pipeline_id: int,
    payload: DataPipelineUpdate,
    db: AsyncSession = Depends(get_db)
):

    try:

        return await data_pipeline_service.update_pipeline(
            db,
            pipeline_id,
            payload
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete("/{pipeline_id}")
async def delete_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):

    try:

        return await data_pipeline_service.delete_pipeline(
            db,
            pipeline_id
        )

    except ValueError as e:
 
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.patch("/{pipeline_id}/activate")
async def activate_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:

        return await data_pipeline_service.activate_pipeline(
            db,
            pipeline_id
        )
    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )



@router.patch("/{pipeline_id}/deactivate")
async def deactivate_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):
    
    try:

        return await data_pipeline_service.deactivate_pipeline(
            db,
            pipeline_id
        )
    
    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )



@router.post("/{pipeline_id}/steps")
async def add_step(
    pipeline_id: int,
    payload: DataPipelineStepCreate,
    db: AsyncSession = Depends(get_db)
):

    payload = payload.model_copy(
        update={
            "pipeline_id": pipeline_id
        }
    )

    try:

        return await data_pipeline_service.add_step(
            db,
            payload
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/{pipeline_id}/steps")
async def list_steps(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await data_pipeline_service.list_steps(
        db,
        pipeline_id
    )


