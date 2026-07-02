from threading import RLock

from app.modules.model_runtime.schemas.loaded_model import (
    LoadedModel
)


class ModelRuntimeRegistry:

    def __init__(self):

        self._models: dict[int, LoadedModel] = {}

        self._lock = RLock()

    def register(

        self,

        model: LoadedModel

    ):

        with self._lock:

            self._models[
                model.release_id
            ] = model

    def get(

        self,

        release_id: int

    ) -> LoadedModel | None:

        return self._models.get(
            release_id
        )

    def remove(

        self,

        release_id: int

    ):

        with self._lock:

            self._models.pop(
                release_id,
                None
            )

    def exists(

        self,

        release_id: int

    ) -> bool:

        return release_id in self._models

    def all(self):

        return list(
            self._models.values()
        )


model_runtime_registry = (
    ModelRuntimeRegistry()
)