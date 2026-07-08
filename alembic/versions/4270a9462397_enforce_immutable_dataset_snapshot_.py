"""enforce immutable dataset snapshot records

Revision ID: 4270a9462397
Revises: 3befdb18def3
Create Date: 2026-07-06 12:32:25.388317
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4270a9462397"
down_revision: Union[str, Sequence[str], None] = "3befdb18def3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Prevent UPDATE or DELETE of dataset records that are already
    covered by any immutable SEALED dataset snapshot boundary.
    """

    op.execute(
        """
        CREATE OR REPLACE FUNCTION
        prevent_immutable_snapshot_record_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM dataset_snapshots AS ds
                WHERE ds.dataset_id = OLD.dataset_id
                  AND ds.status = 'SEALED'
                  AND ds.is_immutable IS TRUE
                  AND ds.max_record_id IS NOT NULL
                  AND OLD.id <= ds.max_record_id
            ) THEN
                RAISE EXCEPTION
                    'Dataset record % is protected by an immutable sealed snapshot',
                    OLD.id
                USING
                    ERRCODE = '55000';
            END IF;

            RETURN OLD;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER
        trg_prevent_immutable_snapshot_record_mutation
        BEFORE UPDATE OR DELETE
        ON dataset_records
        FOR EACH ROW
        EXECUTE FUNCTION
        prevent_immutable_snapshot_record_mutation();
        """
    )


def downgrade() -> None:
    """
    Remove immutable snapshot record mutation protection.
    """

    op.execute(
        """
        DROP TRIGGER IF EXISTS
        trg_prevent_immutable_snapshot_record_mutation
        ON dataset_records;
        """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS
        prevent_immutable_snapshot_record_mutation();
        """
    )