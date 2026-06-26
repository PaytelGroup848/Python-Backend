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

from app.modules.dataset_builder.schemas.dataset_build_request import (
    DatasetBuildRequest
)

from app.modules.dataset_builder.services.dataset_builder_service import (
    dataset_builder_service
)


router = APIRouter(
    prefix="/dataset-builder",
    tags=["Dataset Builder"]
)


@router.post("/build")
async def build_dataset(
    payload: DatasetBuildRequest,
    db: AsyncSession = Depends(get_db)
):

    try:

        return await dataset_builder_service.build_dataset(
            db,
            payload.dataset_id,
            payload.pipeline_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )