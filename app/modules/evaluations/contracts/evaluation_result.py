from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
)


@dataclass(slots=True)
class EvaluationResult:

    metrics: dict[str, Any] = field(
        default_factory=dict,
    )

    summary: dict[str, Any] = field(
        default_factory=dict,
    )