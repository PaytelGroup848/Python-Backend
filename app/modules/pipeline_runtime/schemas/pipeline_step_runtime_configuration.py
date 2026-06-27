from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class PipelineStepRuntimeConfiguration(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

    pipeline_id: UUID

    pipeline_version_id: UUID

    pipeline_step_id: UUID

    execution_id: UUID

    tenant_id: UUID

    organization_id: UUID | None = None

    workspace_id: UUID | None = None

    provider_code: str

    provider_version: str | None = None

    configuration: dict[str, Any] = Field(
        default_factory=dict
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )