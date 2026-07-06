from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pipeline_runtime.models.pipeline_execution_artifact import (
    PipelineExecutionArtifact,
)

from app.modules.pipeline_runtime.models.pipeline_execution_artifact_edge import (
    PipelineExecutionArtifactEdge,
)

from app.modules.pipeline_runtime.repositories.pipeline_execution_artifact_repository import (
    pipeline_execution_artifact_repository,
)

from app.modules.pipeline_runtime.repositories.pipeline_execution_artifact_edge_repository import (
    pipeline_execution_artifact_edge_repository,
)

from app.modules.pipeline_runtime.schemas.storage_object import (
    StorageObject,
)

from app.modules.storage_registry.repositories.storage_instance_repository import (
    storage_instance_repository,
)

from app.shared.constants.pipeline_artifact_status import (
    PipelineArtifactStatus,
)


class PipelineExecutionArtifactService:

    async def publish(
        self,
        db: AsyncSession,
        pipeline_run_id: int,
        producer_step_run_id: int,
        storage_instance_id: int,
        artifact_code: str,
        artifact_type: str,
        storage_object: StorageObject,
        dataset_id: int | None = None,
        corpus_source_id: int | None = None,
        metadata: dict | None = None,
        parent_artifact_ids: Sequence[int] = (),
        relation_type: str | None = None,
    ) -> PipelineExecutionArtifact:

        existing = await (
            pipeline_execution_artifact_repository
            .get_by_code(
                db=db,
                pipeline_run_id=pipeline_run_id,
                artifact_code=artifact_code,
            )
        )

        if existing is not None:

            raise ValueError(
                "Pipeline execution artifact already exists: "
                f"{artifact_code}"
            )

        if parent_artifact_ids and not relation_type:

            raise ValueError(
                "relation_type is required when "
                "parent artifacts are provided"
            )

        storage_instance = await (
            storage_instance_repository
            .get_active_by_id(
                db=db,
                storage_instance_id=(
                    storage_instance_id
                ),
            )
        )

        if storage_instance is None:

            raise ValueError(
                "Active storage instance not found: "
                f"{storage_instance_id}"
            )

        artifact = (
            PipelineExecutionArtifact(
                pipeline_run_id=pipeline_run_id,
                producer_step_run_id=(
                    producer_step_run_id
                ),
                storage_instance_id=(
                    storage_instance_id
                ),
                dataset_id=dataset_id,
                corpus_source_id=(
                    corpus_source_id
                ),
                artifact_code=artifact_code,
                artifact_type=artifact_type,
                storage_provider=(
                    storage_object.storage_provider
                ),
                storage_reference=(
                    storage_object.storage_reference
                ),
                mime_type=(
                    storage_object.mime_type
                ),
                size_bytes=(
                    storage_object.size_bytes
                ),
                checksum=(
                    storage_object.checksum
                ),
                status=(
                    PipelineArtifactStatus.READY
                ),
                metadata_json={
                    **storage_object.metadata,
                    **(metadata or {}),
                },
            )
        )

        artifact = await (
            pipeline_execution_artifact_repository
            .create(
                db=db,
                artifact=artifact,
            )
        )

        for parent_artifact_id in dict.fromkeys(
            parent_artifact_ids
        ):

            if parent_artifact_id == artifact.id:

                raise ValueError(
                    "Artifact cannot be its own parent"
                )

            parent = await (
                pipeline_execution_artifact_repository
                .get_by_id(
                    db=db,
                    artifact_id=parent_artifact_id,
                )
            )

            if parent is None:

                raise ValueError(
                    "Parent pipeline execution artifact "
                    f"not found: {parent_artifact_id}"
                )

            if (
                parent.pipeline_run_id
                !=
                pipeline_run_id
            ):

                raise ValueError(
                    "Cross-run artifact lineage is not "
                    "allowed in pipeline execution lineage"
                )

            existing_edge = await (
                pipeline_execution_artifact_edge_repository
                .get_existing(
                    db=db,
                    parent_artifact_id=(
                        parent_artifact_id
                    ),
                    child_artifact_id=artifact.id,
                    relation_type=relation_type,
                )
            )

            if existing_edge is None:

                await (
                    pipeline_execution_artifact_edge_repository
                    .create(
                        db=db,
                        edge=(
                            PipelineExecutionArtifactEdge(
                                parent_artifact_id=(
                                    parent_artifact_id
                                ),
                                child_artifact_id=(
                                    artifact.id
                                ),
                                relation_type=(
                                    relation_type
                                ),
                            )
                        ),
                    )
                )

        return artifact


pipeline_execution_artifact_service = (
    PipelineExecutionArtifactService()
)