from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class LoadedModel:

    release_id: int

    artifact_id: int

    artifact_path: str

    model_name: str

    tokenizer_name: str | None

    device: str

    loaded_at: datetime

    last_used_at: datetime

    reference_count: int = 0

    status: str = "loaded"

    model: Any = field(default=None, repr=False)

    tokenizer: Any = field(default=None, repr=False)