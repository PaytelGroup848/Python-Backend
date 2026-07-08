import hashlib
import json

from datetime import (
    datetime,
    timezone,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.datasets.models.dataset_snapshot import (
    DatasetSnapshot,
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository,
)

from app.modules.datasets.repositories.dataset_snapshot_repository import (
    dataset_snapshot_repository,
)

from app.modules.datasets.schemas.dataset_snapshot_verification_result import (
    DatasetSnapshotVerificationResult,
)

from app.modules.dataset_records.repositories.dataset_record_repository import (
    dataset_record_repository,
)

from app.shared.exceptions.business_exception import (
    BusinessException,
)


class DatasetSnapshotService:

    @staticmethod
    def _canonical_record_payload(
        record,
    ) -> bytes:

        payload = {
            "id": record.id,
            "dataset_id": record.dataset_id,
            "corpus_source_id": (
                record.corpus_source_id
            ),
            "record_type": record.record_type,
            "status": record.status,
            "record_hash": record.record_hash,
            "validation_score": (
                record.validation_score
            ),
            "input_text": record.input_text,
            "output_text": record.output_text,
            "metadata_json": (
                record.metadata_json
            ),
        }

        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )


    @staticmethod
    def _update_digest(
        digest,
        canonical_payload: bytes,
    ) -> None:

        digest.update(
            len(
                canonical_payload
            )
            .to_bytes(
                8,
                byteorder="big",
                signed=False,
            )
        )

        digest.update(
            canonical_payload
        )


    async def _compute_snapshot_integrity(
        self,
        db: AsyncSession,
        dataset_id: int,
        max_record_id: int | None,
        batch_size: int,
    ) -> tuple[
        int,
        int | None,
        str,
    ]:

        if batch_size <= 0:

            raise BusinessException(
                "Snapshot batch size must be "
                "greater than zero."
            )

        digest = hashlib.sha256()

        last_seen_id: int | None = None

        processed_record_count = 0

        actual_max_record_id: int | None = None

        while True:

            records = await (
                dataset_record_repository
                .list_snapshot_batch(
                    db=db,
                    dataset_id=dataset_id,
                    max_record_id=max_record_id,
                    batch_size=batch_size,
                    last_seen_id=last_seen_id,
                )
            )

            if not records:

                break

            for record in records:

                canonical_payload = (
                    self._canonical_record_payload(
                        record
                    )
                )

                self._update_digest(
                    digest,
                    canonical_payload,
                )

                processed_record_count += 1

                actual_max_record_id = (
                    record.id
                )

            last_seen_id = records[-1].id

        return (
            processed_record_count,
            actual_max_record_id,
            digest.hexdigest(),
        )


    async def create_snapshot(
        self,
        db: AsyncSession,
        dataset_id: int,
        snapshot_code: str,
        batch_size: int,
        snapshot_metadata: dict | None = None,
    ) -> DatasetSnapshot:

        if batch_size <= 0:

            raise BusinessException(
                "Snapshot batch size must be "
                "greater than zero."
            )

        dataset = await (
            dataset_repository
            .get_by_id_for_update(
                db,
                dataset_id,
            )
        )

        if dataset is None:

            raise BusinessException(
                "Dataset not found."
            )

        existing_snapshot = await (
            dataset_snapshot_repository
            .get_by_dataset_and_code(
                db,
                dataset_id,
                snapshot_code,
            )
        )

        if existing_snapshot is not None:

            raise BusinessException(
                "Dataset snapshot code "
                "already exists."
            )

        max_record_id = await (
            dataset_record_repository
            .get_max_id_by_dataset(
                db,
                dataset_id,
            )
        )

        expected_record_count = await (
            dataset_record_repository
            .count_by_dataset_up_to_id(
                db,
                dataset_id,
                max_record_id,
            )
        )

        (
            processed_record_count,
            actual_max_record_id,
            content_hash,
        ) = await self._compute_snapshot_integrity(
            db=db,
            dataset_id=dataset_id,
            max_record_id=max_record_id,
            batch_size=batch_size,
        )

        if (
            processed_record_count
            !=
            expected_record_count
        ):

            raise BusinessException(
                "Dataset changed while snapshot "
                "was being sealed."
            )

        if (
            actual_max_record_id
            !=
            max_record_id
        ):

            raise BusinessException(
                "Dataset snapshot boundary "
                "changed while sealing."
            )

        frozen_at = datetime.now(
            timezone.utc
        ).replace(
            tzinfo=None
        )

        snapshot = DatasetSnapshot(
            dataset_id=dataset.id,
            snapshot_code=snapshot_code,
            status="SEALED",
            record_count=(
                processed_record_count
            ),
            max_record_id=max_record_id,
            content_hash=content_hash,
            snapshot_metadata_json=(
                snapshot_metadata
                or
                {}
            ),
            is_immutable=True,
            frozen_at=frozen_at,
        )

        return await (
            dataset_snapshot_repository
            .create(
                db,
                snapshot,
            )
        )


    async def verify_snapshot(
        self,
        db: AsyncSession,
        snapshot_id: int,
        batch_size: int,
    ) -> DatasetSnapshotVerificationResult:

        if batch_size <= 0:

            raise BusinessException(
                "Snapshot batch size must be "
                "greater than zero."
            )

        snapshot = await (
            dataset_snapshot_repository
            .get_by_id(
                db,
                snapshot_id,
            )
        )

        if snapshot is None:

            raise BusinessException(
                "Dataset snapshot not found."
            )

        if snapshot.status.upper() != "SEALED":

            raise BusinessException(
                "Only SEALED snapshots can "
                "be integrity verified."
            )

        if not snapshot.is_immutable:

            raise BusinessException(
                "Snapshot is not immutable."
            )

        (
            actual_record_count,
            actual_max_record_id,
            actual_content_hash,
        ) = await self._compute_snapshot_integrity(
            db=db,
            dataset_id=snapshot.dataset_id,
            max_record_id=snapshot.max_record_id,
            batch_size=batch_size,
        )

        record_count_matches = (
            actual_record_count
            ==
            snapshot.record_count
        )

        max_record_id_matches = (
            actual_max_record_id
            ==
            snapshot.max_record_id
        )

        content_hash_matches = (
            actual_content_hash
            ==
            snapshot.content_hash
        )

        is_valid = (
            record_count_matches
            and
            max_record_id_matches
            and
            content_hash_matches
        )

        return DatasetSnapshotVerificationResult(
            snapshot_id=snapshot.id,
            dataset_id=snapshot.dataset_id,
            is_valid=is_valid,
            expected_record_count=(
                snapshot.record_count
            ),
            actual_record_count=(
                actual_record_count
            ),
            expected_max_record_id=(
                snapshot.max_record_id
            ),
            actual_max_record_id=(
                actual_max_record_id
            ),
            expected_content_hash=(
                snapshot.content_hash
            ),
            actual_content_hash=(
                actual_content_hash
            ),
            record_count_matches=(
                record_count_matches
            ),
            max_record_id_matches=(
                max_record_id_matches
            ),
            content_hash_matches=(
                content_hash_matches
            ),
        )


dataset_snapshot_service = (
    DatasetSnapshotService()
)