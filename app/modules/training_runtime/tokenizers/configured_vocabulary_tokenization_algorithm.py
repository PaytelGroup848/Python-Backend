import re

from app.modules.training_runtime.contracts.training_tokenization_algorithm import (
    TrainingTokenizationAlgorithm,
)


class ConfiguredVocabularyTokenizationAlgorithm(
    TrainingTokenizationAlgorithm
):

    def encode(
        self,
        text: str,
        configuration: dict,
    ) -> list[int]:

        if not isinstance(text, str):
            raise ValueError(
                "Tokenization input must be a string."
            )

        if not isinstance(configuration, dict):
            raise ValueError(
                "Tokenization algorithm configuration "
                "must be an object."
            )

        vocabulary = (
            configuration.get(
                "vocabulary"
            )
        )

        if not isinstance(vocabulary, dict):
            raise ValueError(
                "Tokenization algorithm configuration "
                "must define 'vocabulary' as an object."
            )

        token_pattern = (
            configuration.get(
                "token_pattern"
            )
        )

        if (
            not isinstance(token_pattern, str)
            or
            not token_pattern.strip()
        ):
            raise ValueError(
                "Tokenization algorithm configuration "
                "must define 'token_pattern'."
            )

        normalization = (
            configuration.get(
                "normalization",
                {}
            )
        )

        if not isinstance(normalization, dict):
            raise ValueError(
                "'normalization' must be an object."
            )

        normalized_text = (
            self._normalize(
                text=text,
                configuration=normalization,
            )
        )

        try:
            pattern = re.compile(
                token_pattern
            )

        except re.error as exc:
            raise ValueError(
                "Configured token pattern is invalid."
            ) from exc

        tokens = [
            match.group(0)
            for match in pattern.finditer(
                normalized_text
            )
        ]

        unknown_token_id = (
            self.get_special_token_id(
                token_name="unk",
                configuration=configuration,
            )
        )

        token_ids: list[int] = []

        for token in tokens:

            token_id = (
                vocabulary.get(
                    token
                )
            )

            if token_id is None:

                if unknown_token_id is None:
                    raise ValueError(
                        "Token is absent from vocabulary "
                        "and no 'unk' special token exists."
                    )

                token_id = (
                    unknown_token_id
                )

            self._validate_token_id(
                token_id=token_id
            )

            token_ids.append(
                token_id
            )

        return token_ids


    def get_special_token_id(
        self,
        token_name: str,
        configuration: dict,
    ) -> int | None:

        if not isinstance(token_name, str):
            raise ValueError(
                "Special token name must be a string."
            )

        if not isinstance(configuration, dict):
            raise ValueError(
                "Tokenization algorithm configuration "
                "must be an object."
            )

        special_tokens = (
            configuration.get(
                "special_tokens",
                {}
            )
        )

        if not isinstance(special_tokens, dict):
            raise ValueError(
                "'special_tokens' must be an object."
            )

        token_definition = (
            special_tokens.get(
                token_name
            )
        )

        if token_definition is None:
            return None

        if isinstance(
            token_definition,
            dict,
        ):
            token_id = (
                token_definition.get(
                    "id"
                )
            )

        else:
            token_id = (
                token_definition
            )

        if token_id is None:
            return None

        self._validate_token_id(
            token_id=token_id
        )

        return token_id


    @staticmethod
    def _normalize(
        text: str,
        configuration: dict,
    ) -> str:

        normalized_text = text

        lowercase = (
            configuration.get(
                "lowercase",
                False,
            )
        )

        strip = (
            configuration.get(
                "strip",
                False,
            )
        )

        if not isinstance(lowercase, bool):
            raise ValueError(
                "'lowercase' must be boolean."
            )

        if not isinstance(strip, bool):
            raise ValueError(
                "'strip' must be boolean."
            )

        if lowercase:
            normalized_text = (
                normalized_text.lower()
            )

        if strip:
            normalized_text = (
                normalized_text.strip()
            )

        return normalized_text


    @staticmethod
    def _validate_token_id(
        token_id: object,
    ) -> None:

        if (
            isinstance(token_id, bool)
            or
            not isinstance(token_id, int)
            or
            token_id < 0
        ):
            raise ValueError(
                "Token IDs must be "
                "non-negative integers."
            )