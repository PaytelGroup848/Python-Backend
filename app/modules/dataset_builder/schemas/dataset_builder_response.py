from pydantic import BaseModel


class DatasetBuilderConfiguration(
    BaseModel
):

    dataset_id: int

    train_split: float

    validation_split: float

    test_split: float

    shuffle: bool

    random_seed: int | None


class DatasetValidationIssue(
    BaseModel
):

    type: str

    severity: str

    message: str

    affected_records: int


class DatasetPreviewSample(
    BaseModel
):

    id: int

    input: str

    output: str


class DatasetBuilderSummary(
    BaseModel
):

    dataset_id: int

    dataset_name: str

    dataset_version: str

    dataset_status: str

    total_records: int

    valid_records: int

    invalid_records: int

    duplicate_records: int

    build_status: str

    last_build_at: str | None

    created_at: str

    updated_at: str


class DatasetBuilderResponse(
    BaseModel
):

    summary: DatasetBuilderSummary

    configuration: DatasetBuilderConfiguration

    validation: list[DatasetValidationIssue]

    preview: list[DatasetPreviewSample]