from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)


@dataclass(slots=True)
class EvaluationExecutionContext:

    db: AsyncSession

    evaluation_job_id: int

    organization_id: int | None = None

    workspace_id: int | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )