import threading

from tokenizers import (
    Tokenizer,
)

from app.modules.training_runtime.contracts.training_tokenization_algorithm import (
    TrainingTokenizationAlgorithm,
)


class SubwordBPETokenizationAlgorithm(
    TrainingTokenizationAlgorithm
):

    _cache: dict[
        str,
        Tokenizer,
    ] = {}

    _cache_lock = (
        threading.RLock()
    )


    def encode(
        self,
        text: str,
        configuration: dict,
    ) -> list[int]:

        if not isinstance(
            text,
            str,
        ):
            raise ValueError(
                "Tokenization input must be "
                "a string."
            )

        tokenizer = (
            self._resolve_tokenizer(
                configuration=configuration
            )
        )

        encoding = (
            tokenizer.encode(
                text,
                add_special_tokens=False,
            )
        )

        token_ids = list(
            encoding.ids
        )

        for token_id in token_ids:

            self._validate_token_id(
                token_id=token_id
            )

        return token_ids


    def get_special_token_id(
        self,
        token_name: str,
        configuration: dict,
    ) -> int | None:

        if (
            not isinstance(
                token_name,
                str,
            )
            or
            not token_name.strip()
        ):
            raise ValueError(
                "Special token name must be "
                "a non-empty string."
            )

        if not isinstance(
            configuration,
            dict,
        ):
            raise ValueError(
                "Tokenization algorithm "
                "configuration must be an object."
            )

        special_tokens = (
            configuration.get(
                "special_tokens",
                {},
            )
        )

        if not isinstance(
            special_tokens,
            dict,
        ):
            raise ValueError(
                "'special_tokens' must be "
                "an object."
            )

        definition = (
            special_tokens.get(
                token_name.strip()
            )
        )

        if definition is None:
            return None

        if isinstance(
            definition,
            dict,
        ):
            token_id = (
                definition.get(
                    "id"
                )
            )

        else:
            token_id = (
                definition
            )

        if token_id is None:
            return None

        self._validate_token_id(
            token_id=token_id
        )

        return token_id


    @classmethod
    def _resolve_tokenizer(
        cls,
        configuration: dict,
    ) -> Tokenizer:

        if not isinstance(
            configuration,
            dict,
        ):
            raise ValueError(
                "Tokenization algorithm "
                "configuration must be an object."
            )

        tokenizer_json = (
            configuration.get(
                "tokenizer_json"
            )
        )

        tokenizer_checksum = (
            configuration.get(
                "tokenizer_checksum"
            )
        )

        if (
            not isinstance(
                tokenizer_json,
                str,
            )
            or
            not tokenizer_json.strip()
        ):
            raise ValueError(
                "Subword BPE tokenizer configuration "
                "must define non-empty "
                "'tokenizer_json'."
            )

        if (
            not isinstance(
                tokenizer_checksum,
                str,
            )
            or
            not tokenizer_checksum.strip()
        ):
            raise ValueError(
                "Subword BPE tokenizer configuration "
                "must define non-empty "
                "'tokenizer_checksum'."
            )

        cache_key = (
            tokenizer_checksum
            .strip()
            .lower()
        )

        with cls._cache_lock:

            tokenizer = (
                cls._cache.get(
                    cache_key
                )
            )

            if tokenizer is None:

                tokenizer = (
                    Tokenizer.from_str(
                        tokenizer_json
                    )
                )

                cls._cache[
                    cache_key
                ] = tokenizer

        return tokenizer


    @staticmethod
    def _validate_token_id(
        token_id: object,
    ) -> None:

        if (
            isinstance(
                token_id,
                bool,
            )
            or
            not isinstance(
                token_id,
                int,
            )
            or
            token_id < 0
        ):
            raise ValueError(
                "Token IDs must be "
                "non-negative integers."
            )