from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TrainingConfigurationResponse(
    BaseModel,
):

    id: int

    configuration_code: str

    version: int

    training_type: str

    runtime_code: str

    configuration_json: dict[
        str,
        Any,
    ]

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }