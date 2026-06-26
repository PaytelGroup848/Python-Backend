from pydantic import BaseModel


class DatasetBuildRequest(
    BaseModel
):

    dataset_id: int

    pipeline_id: int