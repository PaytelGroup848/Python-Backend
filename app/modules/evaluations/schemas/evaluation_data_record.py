from dataclasses import (
    dataclass,
)

from typing import (
    Any,
)


@dataclass(slots=True)
class EvaluationDataRecord:

    input_data: Any

    expected_output: Any

    metadata: dict[str, Any]