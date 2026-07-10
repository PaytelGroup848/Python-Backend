from abc import (
    ABC,
    abstractmethod,
)

from pathlib import (
    Path,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from app.modules.training_runtime.contracts.training_data_stream import (
    TrainingDataStream,
)


class TokenizerTrainerArtifact(
    BaseModel
):

    artifact_code: str

    artifact_type: str

    local_path: Path

    mime_type: str | None = None

    metadata: dict = Field(
        default_factory=dict
    )


    @field_validator(
        "artifact_code",
        "artifact_type",
    )
    @classmethod
    def validate_non_empty_string(
        cls,
        value: str,
    ) -> str:

        normalized_value = (
            value.strip()
        )

        if not normalized_value:
            raise ValueError(
                "Tokenizer trainer artifact identifiers "
                "must be non-empty."
            )

        return normalized_value


    @field_validator(
        "local_path",
    )
    @classmethod
    def validate_local_path(
        cls,
        value: Path,
    ) -> Path:

        if not value.is_absolute():
            raise ValueError(
                "Tokenizer trainer artifact local_path "
                "must be absolute."
            )

        return value


class TokenizerTrainerResult(
    BaseModel
):

    vocabulary_size: int

    artifacts: list[
        TokenizerTrainerArtifact
    ]

    runtime_configuration: dict = Field(
        default_factory=dict
    )

    metadata: dict = Field(
        default_factory=dict
    )


    @field_validator(
        "vocabulary_size",
    )
    @classmethod
    def validate_vocabulary_size(
        cls,
        value: int,
    ) -> int:

        if value <= 0:
            raise ValueError(
                "Tokenizer vocabulary_size must be "
                "greater than zero."
            )

        return value


    @model_validator(
        mode="after",
    )
    def validate_artifacts(
        self,
    ):

        if not self.artifacts:
            raise ValueError(
                "Tokenizer trainer must produce "
                "at least one artifact."
            )

        artifact_codes = [
            artifact.artifact_code
            for artifact in self.artifacts
        ]

        if (
            len(artifact_codes)
            !=
            len(set(artifact_codes))
        ):
            raise ValueError(
                "Tokenizer trainer returned duplicate "
                "artifact_code values."
            )

        return self


class TokenizerTrainer(
    ABC
):

    @abstractmethod
    async def train(
        self,
        training_data: TrainingDataStream,
        configuration: dict,
        output_directory: Path,
    ) -> TokenizerTrainerResult:
        """
        Train a tokenizer from a bounded dataset stream.

        The trainer writes only into the supplied temporary
        output directory and returns a validated description
        of produced artifacts and runtime metadata.

        No artifact is published to permanent storage here.
        Publication belongs to the orchestration layer.
        """
        raise NotImplementedError