"""add chunk and dataset record pipeline steps

Revision ID: 624e043db673
Revises: 3787d1c806e1
Create Date: 2026-07-17 11:28:56.888386
"""

from typing import Sequence, Union
import json

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "624e043db673"
down_revision: Union[str, Sequence[str], None] = "3787d1c806e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    connection = op.get_bind()

    pipeline_id = 4

    # ------------------------------------------------------------------
    # CHUNK STEP
    # ------------------------------------------------------------------

    exists = connection.execute(
        text(
            """
            SELECT 1
            FROM data_pipeline_steps
            WHERE pipeline_id = :pipeline_id
            AND step_code = 'document_chunker'
            """
        ),
        {
            "pipeline_id": pipeline_id
        },
    ).scalar()

    if not exists:

        connection.execute(
            text(
                """
                INSERT INTO data_pipeline_steps
                (
                    pipeline_id,
                    step_order,
                    step_code,
                    step_type,
                    runtime_code,
                    configuration_json,
                    status,
                    created_at,
                    updated_at
                )
                VALUES
                (
                    :pipeline_id,
                    3,
                    'document_chunker',
                    'CHUNK',
                    'RECURSIVE',
                    CAST(:configuration_json AS jsonb),
                    'ACTIVE',
                    NOW(),
                    NOW()
                )
                """
            ),
            {
                "pipeline_id": pipeline_id,
                "configuration_json": json.dumps(
                    {
                        "provider_code": "openai",
                        "provider_version": None,
                        "tokenizer_code": "PLATFORM_SUBWORD_BPE",
                        "nlp_provider_code": "openai",
                        "nlp_model_name": "",
                        "max_characters": 1000,
                        "overlap_characters": 200,
                    }
                ),
            },
        )

    # ------------------------------------------------------------------
    # DATASET RECORD STEP
    # ------------------------------------------------------------------

    exists = connection.execute(
        text(
            """
            SELECT 1
            FROM data_pipeline_steps
            WHERE pipeline_id = :pipeline_id
            AND step_code = 'dataset_record_builder'
            """
        ),
        {
            "pipeline_id": pipeline_id
        },
    ).scalar()

    if not exists:

        connection.execute(
            text(
                """
                INSERT INTO data_pipeline_steps
                (
                    pipeline_id,
                    step_order,
                    step_code,
                    step_type,
                    runtime_code,
                    configuration_json,
                    status,
                    created_at,
                    updated_at
                )
                VALUES
                (
                    :pipeline_id,
                    4,
                    'dataset_record_builder',
                    'DATASET_RECORD',
                    'DEFAULT',
                    '{}'::jsonb,
                    'ACTIVE',
                    NOW(),
                    NOW()
                )
                """
            ),
            {
                "pipeline_id": pipeline_id
            },
        )


def downgrade() -> None:

    connection = op.get_bind()

    connection.execute(
        text(
            """
            DELETE
            FROM data_pipeline_steps
            WHERE pipeline_id = 4
            AND step_code IN
            (
                'document_chunker',
                'dataset_record_builder'
            )
            """
        )
    )