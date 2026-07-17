from pydantic import BaseModel


class DatasetBuildRuntime(BaseModel):

    ingestion_job_id: int

    dataset_id: int

    corpus_source_id: int

    pipeline_id: int

    status: str