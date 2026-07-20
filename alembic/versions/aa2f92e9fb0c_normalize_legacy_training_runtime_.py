"""normalize legacy training runtime configuration

Revision ID: aa2f92e9fb0c
Revises: a511c836067c
Create Date: 2026-07-18
"""
from sqlalchemy.dialects.postgresql import JSONB
from copy import deepcopy
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "aa2f92e9fb0c"
down_revision: Union[str, Sequence[str], None] = "a511c836067c"
branch_labels = None
depends_on = None


REQUIRED_SECTIONS = (
    "execution",
    "training",
    "tokenizer",
    "formatter",
    "model_initialization",
    "optimizer",
    "scheduler",
    "checkpoint",
    "metrics",
    "final_artifact",
)


def prepare_runtime(configuration_json):

    if configuration_json is None:
        runtime = {}
    elif isinstance(configuration_json, dict):
        runtime = deepcopy(configuration_json)
    else:
        runtime = {}

    for section in REQUIRED_SECTIONS:

        value = runtime.get(section)

        if value is None:
            runtime[section] = {}
            continue

        if not isinstance(value, dict):
            runtime[section] = {}

    return runtime


def upgrade() -> None:

    connection = op.get_bind()

    rows = connection.execute(
        sa.text(
            """
            SELECT
                id,
                runtime_code,
                configuration_json
            FROM training_configurations
            WHERE runtime_code='LEGACY_UNCONFIGURED'
            """
        )
    ).mappings()

    for row in rows:

        runtime = prepare_runtime(
            row["configuration_json"]
        )

        connection.execute(
            sa.text(
                """
                UPDATE training_configurations
                SET configuration_json = :configuration_json
                WHERE id = :id
                """
            ).bindparams(
                sa.bindparam(
                    "configuration_json",
                    type_=JSONB,
                )
            ),
            {
                "id": row["id"],
                "configuration_json": runtime,
            },
        )


def downgrade() -> None:
    pass