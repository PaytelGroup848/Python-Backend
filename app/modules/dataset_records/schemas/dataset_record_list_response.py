from pydantic import BaseModel

from app.modules.dataset_records.schemas.dataset_record_response import (
    DatasetRecordResponse,
)


class DatasetRecordListResponse(BaseModel):

    items: list[DatasetRecordResponse]

    total: int

    page: int

    page_size: int

    total_pages: int