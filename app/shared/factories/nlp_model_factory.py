from threading import Lock

import spacy

from spacy.language import Language


class NLPModelFactory:

    def __init__(
        self
    ):

        self._models: dict[
            str,
            Language
        ] = {}

        self._lock = Lock()

    def get_model(
        self,
        model_name: str
    ) -> Language:

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

                model = spacy.load(
                    model_name
                )

                self._models[
                    model_name
                ] = model

        return model


nlp_model_factory = (
    NLPModelFactory()
)