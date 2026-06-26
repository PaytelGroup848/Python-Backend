from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import get_db

from app.modules.dataset_records.schemas.dataset_record_create import (
    DatasetRecordCreate
)

from app.modules.dataset_records.services.dataset_record_service import (
    dataset_record_service
)

router = APIRouter(
    prefix="/dataset-records",
    tags=["Dataset Records"]
)


@router.post("/")
async def create_dataset_record(
    data: DatasetRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    return await (
        dataset_record_service
        .create_dataset_record(
            db,
            data
        )
    )


@router.get("/{dataset_record_id}")
async def get_dataset_record(
    dataset_record_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await (
        dataset_record_service
        .get_dataset_record(
            db,
            dataset_record_id
        )
    )


@router.get("/dataset/{dataset_id}")
async def list_dataset_records(
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await (
        dataset_record_service
        .list_by_dataset(
            db,
            dataset_id
        )
    )