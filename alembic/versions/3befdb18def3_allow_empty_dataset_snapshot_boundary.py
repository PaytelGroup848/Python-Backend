"""allow empty dataset snapshot boundary

Revision ID: 3befdb18def3
Revises: fc2cb6a3359e
Create Date: 2026-07-06 10:38:47.354319

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3befdb18def3"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "fc2cb6a3359e"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "dataset_snapshots",
        "max_record_id",
        existing_type=sa.BIGINT(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "dataset_snapshots",
        "max_record_id",
        existing_type=sa.BIGINT(),
        nullable=False,
    )