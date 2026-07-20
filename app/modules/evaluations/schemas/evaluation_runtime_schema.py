from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
)


@dataclass(slots=True)
class EvaluationRuntime:

    evaluation_job_id: int

    artifact_id: int

    dataset_version_id: int

    evaluation_type: str

    runtime_class: str

    runtime_configuration: dict[str, Any] = field(
        default_factory=dict,
    )