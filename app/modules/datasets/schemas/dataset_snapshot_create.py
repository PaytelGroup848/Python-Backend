from pydantic import BaseModel, Field


class DatasetSnapshotCreate(BaseModel):

    snapshot_code: str = Field(..., description="Unique code identifier for the snapshot (e.g. v1.0, release-2026-08)")

    batch_size: int = Field(default=500, ge=1, le=5000, description="Batch size for computing snapshot hash integrity")

    snapshot_metadata: dict | None = Field(default=None, description="Optional metadata key-value dictionary")
