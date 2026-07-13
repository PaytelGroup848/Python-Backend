from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class TrainingConfigurationCreate(
    BaseModel,
):

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    configuration_code: str = Field(
        min_length=3,
        max_length=150,
    )

    display_name: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    training_type: str = Field(
        min_length=1,
        max_length=100,
    )

    runtime_code: str = Field(
        min_length=1,
        max_length=100,
    )

    configuration_json: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict,
    )

    created_by: str = Field(
        min_length=1,
        max_length=150,
    )

    @field_validator(
        "configuration_code",
        "display_name",
        "training_type",
        "runtime_code",
        "created_by",
    )
    @classmethod
    def validate_non_empty(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty."
            )

        return value