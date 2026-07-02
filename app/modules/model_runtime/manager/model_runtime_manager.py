from datetime import datetime

from app.modules.model_runtime.loader.artifact_loader import (
    artifact_loader
)

from app.modules.model_runtime.loader.model_loader import (
    model_loader
)

from app.modules.model_runtime.loader.tokenizer_loader import (
    tokenizer_loader
)

from app.modules.model_runtime.registry.model_runtime_registry import (
    model_runtime_registry
)

from app.modules.model_runtime.schemas.loaded_model import (
    LoadedModel
)


class ModelRuntimeManager:

    async def load_model(

        self,

        release_id: int,

        artifact_id: int,

        artifact_path: str,

        model_name: str,

        tokenizer_path: str | None = None,

        device: str = "cpu"

    ) -> LoadedModel:

        runtime = model_runtime_registry.get(
            release_id
        )

        if runtime:

            runtime.reference_count += 1

            runtime.last_used_at = datetime.utcnow()

            return runtime

        artifact = artifact_loader.resolve(
            artifact_path
        )

        tokenizer = None

        if tokenizer_path:

            tokenizer = tokenizer_loader.load(
                tokenizer_path
            )

        model = model_loader.load(
            str(artifact)
        )

        runtime = LoadedModel(

            release_id=release_id,

            artifact_id=artifact_id,

            artifact_path=str(artifact),

            model_name=model_name,

            tokenizer_name=tokenizer_path,

            device=device,

            loaded_at=datetime.utcnow(),

            last_used_at=datetime.utcnow(),

            reference_count=1,

            status="loaded"

        )

        #
        # Temporary placeholders
        #
        runtime.model = model

        runtime.tokenizer = tokenizer

        model_runtime_registry.register(
            runtime
        )

        return runtime

    async def unload_model(

        self,

        release_id: int

    ):

        runtime = model_runtime_registry.get(
            release_id
        )

        if runtime is None:

            return

        model_runtime_registry.remove(
            release_id
        )

    async def reload_model(

        self,

        release_id: int,

        artifact_id: int,

        artifact_path: str,

        model_name: str,

        tokenizer_path: str | None = None,

        device: str = "cpu"

    ):

        await self.unload_model(
            release_id
        )

        return await self.load_model(

            release_id=release_id,

            artifact_id=artifact_id,

            artifact_path=artifact_path,

            model_name=model_name,

            tokenizer_path=tokenizer_path,

            device=device

        )

    def get_loaded_model(

        self,

        release_id: int

    ):

        runtime = model_runtime_registry.get(
            release_id
        )

        if runtime:

            runtime.last_used_at = datetime.utcnow()

        return runtime

    def is_loaded(

        self,

        release_id: int

    ) -> bool:

        return model_runtime_registry.exists(
            release_id
        )


model_runtime_manager = (
    ModelRuntimeManager()
)