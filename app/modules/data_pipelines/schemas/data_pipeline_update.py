from typing import Optional

from pydantic import BaseModel


class DataPipelineUpdate(
    BaseModel
):

    name: Optional[str] = None

    dataset_id: Optional[int] = None

    version: Optional[str] = None

    status: Optional[str] = None