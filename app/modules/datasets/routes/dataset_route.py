from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import (
    get_db,
)

from app.modules.datasets.schemas.dataset_create import (
    DatasetCreate,
)

from app.modules.datasets.schemas.dataset_update import (
    DatasetUpdate,
)

from app.modules.datasets.schemas.dataset_response import (
    DatasetResponse,
)

from app.modules.datasets.schemas.dataset_list_response import (
    DatasetListResponse,
)

from app.modules.datasets.services.dataset_service import (
    dataset_service,
)

from app.modules.datasets.services.dataset_snapshot_service import (
    dataset_snapshot_service,
)

from app.modules.datasets.schemas.dataset_snapshot_response import (
    DatasetSnapshotResponse,
)
router = APIRouter(

    prefix="/datasets",

    tags=["Datasets"],

)


@router.post(

    "",

    response_model=DatasetResponse,

    status_code=status.HTTP_201_CREATED,

)
async def create_dataset(

    data: DatasetCreate,

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await (
        dataset_service.create_dataset(
            db=db,
            data=data,
        )
    )


@router.get(

    "",

    response_model=DatasetListResponse,

)
async def list_datasets(

    page: int = Query(
        default=1,
        ge=1,
    ),

    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    search: str | None = Query(
        default=None,
    ),

    domain: str | None = Query(
        default=None,
    ),

    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),

    sort: str = Query(
        default="created_at",
    ),

    direction: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
    ),

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await (
        dataset_service.list_datasets(

            db=db,

            page=page,

            page_size=page_size,

            search=search,

            domain=domain,

            status=status_filter,

            sort=sort,

            direction=direction,

        )
    )


@router.get(

    "/{dataset_id}",

    response_model=DatasetResponse,

)
async def get_dataset(

    dataset_id: int,

    db: AsyncSession = Depends(
        get_db
    ),

):

    dataset = await (
        dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
        )
    )

    if dataset is None:

        raise HTTPException(

            status_code=404,

            detail="Dataset not found",

        )

    return dataset


@router.patch(

    "/{dataset_id}",

    response_model=DatasetResponse,

)
async def update_dataset(

    dataset_id: int,

    data: DatasetUpdate,

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await (
        dataset_service.update_dataset(
            db=db,
            dataset_id=dataset_id,
            data=data,
        )
    )


@router.delete(

    "/{dataset_id}",

    status_code=status.HTTP_204_NO_CONTENT,

)
async def delete_dataset(

    dataset_id: int,

    db: AsyncSession = Depends(
        get_db
    ),

):

    await (
        dataset_service.delete_dataset(
            db=db,
            dataset_id=dataset_id,
        )
    )


from app.modules.datasets.schemas.dataset_snapshot_create import (
    DatasetSnapshotCreate,
)


@router.get(
    "/{dataset_id}/snapshots",
    response_model=list[DatasetSnapshotResponse],
)
async def list_dataset_snapshots(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
):

    return await dataset_snapshot_service.list_dataset_snapshots(
        db=db,
        dataset_id=dataset_id,
    )


@router.post(
    "/{dataset_id}/snapshots",
    response_model=DatasetSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dataset_snapshot(
    dataset_id: int,
    data: DatasetSnapshotCreate,
    db: AsyncSession = Depends(get_db),
):
    return await dataset_snapshot_service.create_snapshot(
        db=db,
        dataset_id=dataset_id,
        snapshot_code=data.snapshot_code,
        batch_size=data.batch_size,
        snapshot_metadata=data.snapshot_metadata,
    )