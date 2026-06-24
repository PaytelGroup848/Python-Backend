from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.ingestion.services.ingestion_job_service import (
    ingestion_job_service
)

from app.modules.ingestion.schemas.ingestion_job_create import (
    IngestionJobCreate
)

router = APIRouter(

    prefix="/ingestion",

    tags=["Ingestion"]
)


@router.post("/")
async def create_ingestion_job(

    data: IngestionJobCreate,

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (

        ingestion_job_service
        .create_ingestion_job(
            db,
            data
        )
    )


@router.get("/{ingestion_job_id}")
async def get_ingestion_job(

    ingestion_job_id: int,

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (

        ingestion_job_service
        .get_ingestion_job(
            db,
            ingestion_job_id
        )
    )