from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class TrainingConfigurationUpdate(
    BaseModel,
):

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    display_name: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    configuration_json: dict[
        str,
        Any,
    ] | None = None

    updated_by: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    @field_validator(
        "display_name",
        "updated_by",
    )
    @classmethod
    def validate_string(
        cls,
        value: str | None,
    ):

        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty."
            )

        return value