from pydantic import BaseModel


class DatasetBuildResponse(
    BaseModel
):

    dataset_id: int

    pipeline_id: int

    total_records: int

    processed_records: int

    failed_records: int

    status: str