from threading import Lock
from typing import Any

from sentence_transformers import SentenceTransformer


class EmbeddingModelFactory:

    def __init__(
        self
    ):

        self._models: dict[
            str,
            Any
        ] = {}

        self._lock = Lock()

    def get_sentence_transformer(
        self,
        model_name: str
    ) -> SentenceTransformer:

        model = self._models.get(
            model_name
        )

        if model is not None:

            return model

        with self._lock:

            model = self._models.get(
                model_name
            )

            if model is None:

                model = SentenceTransformer(
                    model_name
                )

                self._models[
                    model_name
                ] = model

        return model

    def clear_cache(
        self
    ) -> None:

        self._models.clear()


embedding_model_factory = (
    EmbeddingModelFactory()
)