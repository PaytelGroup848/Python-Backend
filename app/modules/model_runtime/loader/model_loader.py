import io

import torch

from datetime import datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.model_artifacts.models.model_artifact import (
    ModelArtifact,
)

from app.modules.storage_runtime.services.storage_resolution_service import (
    storage_resolution_service,
)

from app.modules.training_runtime.services.training_runtime_service import (
    training_runtime_service,
)

from app.modules.training_runtime.services.training_model_initialization_service import (
    training_model_initialization_service,
)

from app.modules.model_runtime.schemas.loaded_model import (
    LoadedModel,
)


class ModelLoader:

    async def load(

        self,

        db: AsyncSession,

        artifact: ModelArtifact,

    ) -> LoadedModel:

        resolved_storage = await (

            storage_resolution_service.resolve(

                db=db,

                storage_instance_id=(
                    artifact.storage_instance_id
                ),

            )

        )

        stream = await (

            resolved_storage.runtime.open_read(

                artifact.storage_reference

            )

        )

        artifact_bytes = stream.read()

        payload = torch.load(

            io.BytesIO(
                artifact_bytes
            ),

            map_location="cpu",

        )

        training_runtime = await (

            training_runtime_service.load_runtime(

                db=db,

                training_job_id=(
                    artifact.training_job_id
                ),

            )

        )

        model = await (

            training_model_initialization_service.initialize(

                runtime=training_runtime,

            )

        )

        if "model_state_dict" not in payload:

            raise ValueError(
                "Artifact does not contain model_state_dict."
            )

        model.load_state_dict(

            payload["model_state_dict"]

        )

        return LoadedModel(

            release_id=0,

            artifact_id=artifact.id,

            artifact_path=(
                artifact.artifact_path
                or
                artifact.storage_reference
                or
                ""
            ),

            model_name=(
                training_runtime.base_model_code
            ),

            tokenizer_name=(
                training_runtime.tokenizer_version
            ),

            device="cpu",

            loaded_at=datetime.utcnow(),

            last_used_at=datetime.utcnow(),

            reference_count=1,

            status="loaded",

            model=model,

            tokenizer=None,

            artifact_metadata=(
                payload.get(
                    "artifact_metadata",
                    {},
                )
            ),

            strategy_metadata=(
                payload.get(
                    "strategy_metadata",
                    {},
                )
            ),

            lineage=(
                payload.get(
                    "lineage",
                    {},
                )
            ),

        )


model_loader = (
    ModelLoader()
)