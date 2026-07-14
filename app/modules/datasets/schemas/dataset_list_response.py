from pydantic import BaseModel

from app.modules.datasets.schemas.dataset_response import (
    DatasetResponse,
)


class DatasetListResponse(
    BaseModel
):

    items: list[
        DatasetResponse
    ]

    total: int

    page: int

    page_size: int

    total_pages: int