from pydantic import (
    BaseModel,
    ConfigDict
)


class BaseProviderConfiguration(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

    provider_code: str

    provider_version: str | None = None