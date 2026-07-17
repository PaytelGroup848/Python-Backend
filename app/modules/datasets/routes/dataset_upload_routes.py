from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import (
    get_db,
)

from app.modules.datasets.schemas.dataset_upload_request import (
    DatasetUploadRequest,
)

from app.modules.datasets.services.dataset_upload_service import (
    dataset_upload_service,
)

router = APIRouter(

    prefix="/dataset-uploads",

    tags=[
        "Dataset Uploads",
    ],

)

@router.post("")
async def upload_dataset(

    dataset_id: int = Form(...),

    file: UploadFile = File(...),

    created_by: str | None = Form(
        default=None,
    ),

    db: AsyncSession = Depends(
        get_db,
    ),

):
    content = await file.read()

    request = DatasetUploadRequest(

        dataset_id=dataset_id,

        original_file_name=(
            file.filename
            or
            "unknown"
        ),

        mime_type=(
            file.content_type
            or
            "application/octet-stream"
        ),

        file_size=len(content),

        content=content,

        created_by=created_by,

    )

    return await (
        dataset_upload_service
        .upload(
            db=db,
            request=request,
        )
    )

@router.get("")
async def list_dataset_uploads(

    dataset_id: int,

    db: AsyncSession = Depends(
        get_db,
    ),

):

    return await (
        dataset_upload_service
        .list_by_dataset(
            db=db,
            dataset_id=dataset_id,
        )
    )

@router.get("/{upload_id}")
async def get_dataset_upload(

    upload_id: int,

    db: AsyncSession = Depends(
        get_db,
    ),

):

    return await (
        dataset_upload_service
        .get_by_id(
            db=db,
            upload_id=upload_id,
        )
    )

@router.delete("/{upload_id}")
async def delete_dataset_upload(

    upload_id: int,

    db: AsyncSession = Depends(
        get_db,
    ),

):

    await (
        dataset_upload_service
        .delete(
            db=db,
            upload_id=upload_id,
        )
    )

    return {
        "message": "Dataset upload deleted successfully."
    }

