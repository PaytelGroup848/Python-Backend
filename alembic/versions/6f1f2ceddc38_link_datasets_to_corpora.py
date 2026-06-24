"""link datasets to corpora

Revision ID: 6f1f2ceddc38
Revises: 53e37ab4e9f2
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "6f1f2ceddc38"
down_revision: Union[str, Sequence[str], None] = "53e37ab4e9f2"
branch_labels = None
depends_on = None

def upgrade():


    op.add_column(
        "datasets",
        sa.Column(
            "corpus_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_index(
        "ix_datasets_corpus_id",
        "datasets",
        ["corpus_id"],
        unique=False
    )

    op.create_foreign_key(
        "fk_dataset_corpus_id",
        "datasets",
        "corpora",
        ["corpus_id"],
        ["id"]
    )


def downgrade():


    op.drop_constraint(
        "fk_dataset_corpus_id",
        "datasets",
        type_="foreignkey"
    )

    op.drop_index(
        "ix_datasets_corpus_id",
        table_name="datasets"
    )

    op.drop_column(
        "datasets",
        "corpus_id"
    )



