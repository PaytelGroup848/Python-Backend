from dataclasses import (
    dataclass,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)


@dataclass(
    slots=True,
)
class TrainingExecutionContext:

    db: AsyncSession

    organization_id: int | None = None

    workspace_id: int | None = None