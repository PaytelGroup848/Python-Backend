from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.datasets.models.dataset_upload import (
    DatasetUpload,
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository,
)

from app.modules.datasets.repositories.dataset_upload_repository import (
    dataset_upload_repository,
)

from app.modules.datasets.schemas.dataset_upload_request import (
    DatasetUploadRequest,
)

from app.modules.datasets.services.dataset_storage_key_service import (
    dataset_storage_key_service,
)

from app.modules.datasets.services.dataset_storage_service import (
    dataset_storage_service,
)

from app.shared.exceptions.business_exception import (
    BusinessException,
)

class DatasetUploadService:

    async def upload(

        self,

        db: AsyncSession,

        request: DatasetUploadRequest,

    ):
        dataset = await (
            dataset_repository
            .get_by_id(
                db=db,
                dataset_id=request.dataset_id,
            )
        )

        if dataset is None:

            raise BusinessException(
                "Dataset not found."
            )
        
        resolved_storage = await (
            dataset_storage_service
            .resolve_platform_storage(
                db=db,
            )
        )

        runtime = (
            resolved_storage.runtime
        )

        object_key = (
            dataset_storage_key_service
            .generate_upload_key(
                dataset_id=request.dataset_id,
                original_file_name=(
                    request.original_file_name
                ),
            )
        )

        

        try:

            storage_object = await (
                runtime.publish_bytes(
                    content=request.content,
                    object_key=object_key,
                    mime_type=request.mime_type,
                    metadata=(
                        request.metadata_json
                        or
                        {}
                    ),
                )
            )

            dataset_upload = DatasetUpload(

                dataset_id=request.dataset_id,

                original_file_name=(
                    request.original_file_name
                ),

                stored_file_name=(
                    Path(
                        object_key
                    ).name
                ),

                file_extension=(
                    Path(
                        request.original_file_name
                    )
                    .suffix
                    .lower()
                ),

                mime_type=(
                    storage_object.mime_type
                    or
                    request.mime_type
                ),

                file_size=(
                    storage_object.size_bytes
                    or
                    request.file_size
                ),

                storage_provider=(
                    storage_object.storage_provider
                ),

                storage_reference=(
                    storage_object.storage_reference
                ),

                checksum=(
                    storage_object.checksum
                ),

                upload_status="UPLOADED",

                ingestion_status="PENDING",

                metadata_json=(
                    storage_object.metadata
                ),

                created_by=request.created_by,
            )

            dataset_upload = await (
                dataset_upload_repository
                .create(
                    db=db,
                    dataset_upload=dataset_upload,
                )
            )

            await db.commit()

            return dataset_upload

        except Exception as exc:

            await db.rollback()

            raise BusinessException(
                "Failed to upload dataset."
            ) from exc
    
    async def get_by_id(

        self,

        db: AsyncSession,

        upload_id: int,

    ):

        upload = await (
            dataset_upload_repository
            .get_by_id(
                db=db,
                upload_id=upload_id,
            )
        )

        if upload is None:

            raise BusinessException(
                "Dataset upload not found."
            )

        return upload
    
    async def list_by_dataset(

        self,

        db: AsyncSession,

        dataset_id: int,

    ):

        return await (
            dataset_upload_repository
            .list_by_dataset(
                db=db,
                dataset_id=dataset_id,
            )
        )
    
    async def delete(

        self,

        db: AsyncSession,

        upload_id: int,

    ):

        upload = await (
            dataset_upload_repository
            .get_by_id(
                db=db,
                upload_id=upload_id,
            )
        )

        if upload is None:

            raise BusinessException(
                "Dataset upload not found."
            )

        resolved_storage = await (
            dataset_storage_service
            .resolve_platform_storage(
                db=db,
            )
        )

        await (
            resolved_storage.runtime
            .delete(
                upload.storage_reference,
            )
        )

        await (
            dataset_upload_repository
            .mark_deleted(
                db=db,
                dataset_upload=upload,
            )
        )

        await db.commit()
            


dataset_upload_service = (
    DatasetUploadService()
)
        