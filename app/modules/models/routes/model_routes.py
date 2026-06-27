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

from app.modules.models.services.model_service import (
    model_service
)

from app.modules.models.schemas.model_schema import (
    CreateModelRequest,
    UpdateModelRequest,
    ModelListResponse
)


router = APIRouter(

    prefix="/models",

    tags=["Models"]
)


@router.post("")
async def create_model(

    payload: CreateModelRequest,

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        model_service
        .create_model(

            db=db,

            code=payload.code,

            display_name=payload.display_name,

            provider_id=payload.provider_id,

            description=payload.description

        )
    )


@router.get(
    "",
    response_model=
    ModelListResponse
)
async def get_models(

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        model_service
        .get_models(db)
    )


@router.get(
    "/{code}"
)
async def get_model(

    code: str,

    db: AsyncSession = Depends(
        get_db
    )
):

    model = await (
        model_service.get_model(
            db,
            code
        )
    )

    if not model:

        raise HTTPException(

            status_code=404,

            detail=
            "Model not found"
        )

    return model


@router.patch(
    "/{code}"
)
async def update_model(

    code: str,

    payload: UpdateModelRequest,

    db: AsyncSession = Depends(
        get_db
    )
):

    model = await (
        model_service.update_model(
            db,
            code,
            payload
        )
    )

    if not model:

        raise HTTPException(

            status_code=404,

            detail=
            "Model not found"
        )

    return model


@router.delete(
    "/{code}"
)
async def delete_model(

    code: str,

    db: AsyncSession = Depends(
        get_db
    )
):

    deleted = await (
        model_service.delete_model(
            db,
            code
        )
    )

    if not deleted:

        raise HTTPException(

            status_code=404,

            detail=
            "Model not found"
        )

    return {

        "message":
        "Model deleted"
    }