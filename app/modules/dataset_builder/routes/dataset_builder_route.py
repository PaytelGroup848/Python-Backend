from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import (
    get_db,
)

from app.modules.dataset_builder.schemas.dataset_build_request import (
    DatasetBuildRequest,
)

from app.modules.dataset_builder.schemas.dataset_builder_response import (
    DatasetBuilderResponse,
)

from app.modules.dataset_builder.schemas.dataset_build_response import (
    DatasetBuildResponse,
)

from app.modules.dataset_builder.services.dataset_builder_service import (
    dataset_builder_service,
)

router = APIRouter(

    prefix="/datasets",

    tags=["Dataset Builder"],

)


@router.get(

    "/{dataset_id}/builder",

    response_model=DatasetBuilderResponse,

)
async def get_dataset_builder(

    dataset_id: int,

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await (

        dataset_builder_service.get_builder(

            db=db,

            dataset_id=dataset_id,

        )

    )


@router.post(
    "/{dataset_id}/builder/build",
    response_model=DatasetBuildResponse,
)
async def build_dataset(

    dataset_id: int,

    payload: DatasetBuildRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    try:

        return await (

            dataset_builder_service.build_dataset(

                db=db,

                dataset_id=dataset_id,

                pipeline_id=payload.pipeline_id,

            )

        )

    except ValueError as exc:

        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )