from pydantic import (
    BaseModel,
)


class DatasetSnapshotVerificationResult(
    BaseModel
):

    snapshot_id: int

    dataset_id: int

    is_valid: bool

    expected_record_count: int

    actual_record_count: int

    expected_max_record_id: int | None

    actual_max_record_id: int | None

    expected_content_hash: str

    actual_content_hash: str

    record_count_matches: bool

    max_record_id_matches: bool

    content_hash_matches: bool