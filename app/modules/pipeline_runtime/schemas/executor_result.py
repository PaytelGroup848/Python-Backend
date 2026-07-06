from dataclasses import (
    dataclass,
    field,
)

from typing import Any


@dataclass(
    slots=True,
)
class ExecutorResult:

    metrics: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    outputs: list[
        dict[
            str,
            Any,
        ]
    ] = field(
        default_factory=list
    )