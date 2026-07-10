import json
import re

from collections import Counter
from pathlib import Path

from app.modules.tokenizers.contracts.tokenizer_trainer import (
    TokenizerTrainer,
    TokenizerTrainerArtifact,
    TokenizerTrainerResult,
)

from app.modules.training_runtime.contracts.training_data_stream import (
    TrainingDataStream,
)


class ConfiguredVocabularyTokenizerTrainer(
    TokenizerTrainer
):

    async def train(
        self,
        training_data: TrainingDataStream,
        configuration: dict,
        output_directory: Path,
    ) -> TokenizerTrainerResult:

        if not isinstance(configuration, dict):
            raise ValueError(
                "Tokenizer trainer configuration "
                "must be an object."
            )

        token_pattern = configuration.get(
            "token_pattern"
        )

        if (
            not isinstance(token_pattern, str)
            or
            not token_pattern.strip()
        ):
            raise ValueError(
                "Tokenizer trainer configuration "
                "must define 'token_pattern'."
            )

        try:
            compiled_pattern = re.compile(
                token_pattern
            )
        except re.error as exc:
            raise ValueError(
                "Configured token pattern is invalid."
            ) from exc

        normalization = configuration.get(
            "normalization",
            {},
        )

        if not isinstance(normalization, dict):
            raise ValueError(
                "'normalization' must be an object."
            )

        lowercase = normalization.get(
            "lowercase",
            False,
        )

        strip = normalization.get(
            "strip",
            False,
        )

        if not isinstance(lowercase, bool):
            raise ValueError(
                "'lowercase' must be boolean."
            )

        if not isinstance(strip, bool):
            raise ValueError(
                "'strip' must be boolean."
            )

        vocabulary_limit = configuration.get(
            "vocabulary_limit"
        )

        if (
            isinstance(vocabulary_limit, bool)
            or
            not isinstance(vocabulary_limit, int)
            or
            vocabulary_limit <= 0
        ):
            raise ValueError(
                "'vocabulary_limit' must be "
                "a positive integer."
            )

        minimum_frequency = configuration.get(
            "minimum_frequency",
            1,
        )

        if (
            isinstance(minimum_frequency, bool)
            or
            not isinstance(minimum_frequency, int)
            or
            minimum_frequency <= 0
        ):
            raise ValueError(
                "'minimum_frequency' must be "
                "a positive integer."
            )

        special_tokens = configuration.get(
            "special_tokens",
            {},
        )

        if not isinstance(special_tokens, dict):
            raise ValueError(
                "'special_tokens' must be an object."
            )

        normalized_special_tokens = (
            self._validate_special_tokens(
                special_tokens=special_tokens,
            )
        )

        token_counter: Counter[str] = Counter()

        source_record_count = 0

        async for batch in training_data.iter_batches():

            for record in batch.records:

                source_record_count += 1

                texts = [
                    record.input_text,
                ]

                if record.output_text is not None:
                    texts.append(
                        record.output_text
                    )

                for text in texts:

                    normalized_text = self._normalize(
                        text=text,
                        lowercase=lowercase,
                        strip=strip,
                    )

                    token_counter.update(
                        match.group(0)
                        for match
                        in compiled_pattern.finditer(
                            normalized_text
                        )
                    )

        if source_record_count <= 0:
            raise ValueError(
                "Tokenizer training dataset "
                "must not be empty."
            )

        reserved_ids = {
            definition["id"]
            for definition
            in normalized_special_tokens.values()
        }

        vocabulary = {}

        for definition in (
            normalized_special_tokens.values()
        ):
            vocabulary[
                definition["token"]
            ] = definition["id"]

        candidates = [
            (
                token,
                frequency,
            )
            for token, frequency
            in token_counter.items()
            if frequency >= minimum_frequency
            and token not in vocabulary
        ]

        candidates.sort(
            key=lambda item: (
                -item[1],
                item[0],
            )
        )

        next_token_id = 0

        for token, _ in candidates:

            if len(vocabulary) >= vocabulary_limit:
                break

            while next_token_id in reserved_ids:
                next_token_id += 1

            vocabulary[token] = next_token_id

            next_token_id += 1

        if not vocabulary:
            raise ValueError(
                "Tokenizer training produced "
                "an empty vocabulary."
            )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        artifact_path = (
            output_directory
            /
            "vocabulary.json"
        ).resolve()

        artifact_payload = {
            "format_version": 1,
            "vocabulary": vocabulary,
            "special_tokens": (
                normalized_special_tokens
            ),
            "token_pattern": token_pattern,
            "normalization": {
                "lowercase": lowercase,
                "strip": strip,
            },
        }

        artifact_path.write_text(
            json.dumps(
                artifact_payload,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )

        runtime_configuration = {
            "vocabulary": vocabulary,
            "special_tokens": {
                name: {
                    "id": definition["id"],
                    "token": definition["token"],
                }
                for name, definition
                in normalized_special_tokens.items()
            },
            "token_pattern": token_pattern,
            "normalization": {
                "lowercase": lowercase,
                "strip": strip,
            },
        }

        return TokenizerTrainerResult(
            vocabulary_size=len(vocabulary),

            artifacts=[
                TokenizerTrainerArtifact(
                    artifact_code="vocabulary.json",
                    artifact_type=(
                        "CONFIGURED_VOCABULARY"
                    ),
                    local_path=artifact_path,
                    mime_type="application/json",
                    metadata={
                        "format_version": 1,
                        "source_record_count": (
                            source_record_count
                        ),
                    },
                )
            ],

            runtime_configuration=(
                runtime_configuration
            ),

            metadata={
                "source_record_count": (
                    source_record_count
                ),
                "observed_unique_tokens": (
                    len(token_counter)
                ),
                "minimum_frequency": (
                    minimum_frequency
                ),
                "vocabulary_limit": (
                    vocabulary_limit
                ),
            },
        )


    @staticmethod
    def _normalize(
        text: str,
        lowercase: bool,
        strip: bool,
    ) -> str:

        if not isinstance(text, str):
            raise ValueError(
                "Tokenizer training text "
                "must be a string."
            )

        normalized = text

        if lowercase:
            normalized = normalized.lower()

        if strip:
            normalized = normalized.strip()

        return normalized


    @staticmethod
    def _validate_special_tokens(
        special_tokens: dict,
    ) -> dict:

        normalized = {}

        seen_ids = set()
        seen_tokens = set()

        for name, definition in (
            special_tokens.items()
        ):

            if (
                not isinstance(name, str)
                or
                not name.strip()
            ):
                raise ValueError(
                    "Special token names must "
                    "be non-empty strings."
                )

            if not isinstance(definition, dict):
                raise ValueError(
                    "Special token definitions "
                    "must be objects."
                )

            token = definition.get("token")
            token_id = definition.get("id")

            if (
                not isinstance(token, str)
                or
                not token
            ):
                raise ValueError(
                    "Special token definition "
                    "must define 'token'."
                )

            if (
                isinstance(token_id, bool)
                or
                not isinstance(token_id, int)
                or
                token_id < 0
            ):
                raise ValueError(
                    "Special token definition "
                    "must define a non-negative "
                    "integer 'id'."
                )

            if token_id in seen_ids:
                raise ValueError(
                    "Special token IDs must "
                    "be unique."
                )

            if token in seen_tokens:
                raise ValueError(
                    "Special token values must "
                    "be unique."
                )

            seen_ids.add(token_id)
            seen_tokens.add(token)

            normalized[name.strip()] = {
                "token": token,
                "id": token_id,
            }

        return normalized