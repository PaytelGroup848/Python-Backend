from pathlib import Path
from uuid import uuid4


class DatasetStorageKeyService:

    DATASET_ROOT = "datasets"

    UPLOAD_DIRECTORY = "uploads"

    def generate_upload_key(
        self,
        dataset_id: int,
        original_file_name: str,
    ) -> str:

        suffix = (
            Path(
                original_file_name
            )
            .suffix
            .lower()
        )

        object_name = (
            f"{uuid4().hex}{suffix}"
        )

        return "/".join(

            [

                self.DATASET_ROOT,

                str(
                    dataset_id
                ),

                self.UPLOAD_DIRECTORY,

                object_name,

            ]

        )

    def generate_ingestion_key(
        self,
        dataset_id: int,
        upload_id: int,
        artifact_name: str,
    ) -> str:

        return "/".join(

            [

                self.DATASET_ROOT,

                str(
                    dataset_id
                ),

                "ingestion",

                str(
                    upload_id
                ),

                artifact_name,

            ]

        )

    def generate_snapshot_key(
        self,
        dataset_id: int,
        snapshot_id: int,
        artifact_name: str,
    ) -> str:

        return "/".join(

            [

                self.DATASET_ROOT,

                str(
                    dataset_id
                ),

                "snapshots",

                str(
                    snapshot_id
                ),

                artifact_name,

            ]

        )

    def generate_training_key(
        self,
        training_job_id: int,
        artifact_name: str,
    ) -> str:

        return "/".join(

            [

                "training",

                str(
                    training_job_id
                ),

                artifact_name,

            ]

        )


dataset_storage_key_service = (
    DatasetStorageKeyService()
)