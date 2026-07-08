"""add versioned training configurations

Revision ID: 431dfa4903d9
Revises: 5bab4793daa1
Create Date: 2026-07-06 09:56:34.151989
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "431dfa4903d9"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "5bab4793daa1"

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

    op.create_table(
        "training_configurations",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "configuration_code",
            sa.String(length=150),
            nullable=False,
        ),

        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "training_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "runtime_code",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "configuration_json",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            server_default="{}",
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text(
                "now()"
            ),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "configuration_code",
            "version",
            name=(
                "uq_training_configuration_"
                "code_version"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_training_configurations_"
            "configuration_code"
        ),
        "training_configurations",
        ["configuration_code"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_training_configurations_id"
        ),
        "training_configurations",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_training_configurations_"
            "is_active"
        ),
        "training_configurations",
        ["is_active"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_training_configurations_"
            "runtime_code"
        ),
        "training_configurations",
        ["runtime_code"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_training_configurations_"
            "training_type"
        ),
        "training_configurations",
        ["training_type"],
        unique=False,
    )

    op.add_column(
        "training_jobs",
        sa.Column(
            "training_configuration_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    connection = op.get_bind()

    legacy_groups = connection.execute(
        sa.text(
            """
            SELECT DISTINCT
                tj.training_provider_id,
                tj.training_type,
                tp.code AS provider_code,
                tp.runtime_class
            FROM training_jobs tj
            JOIN training_providers tp
              ON tp.id = tj.training_provider_id
            ORDER BY
                tj.training_provider_id,
                tj.training_type
            """
        )
    ).mappings().all()

    for group in legacy_groups:

        provider_id = (
            group[
                "training_provider_id"
            ]
        )

        training_type = (
            group[
                "training_type"
            ]
        )

        provider_code = (
            group[
                "provider_code"
            ]
        )

        runtime_class = (
            group[
                "runtime_class"
            ]
        )

        configuration_code = (
            "legacy-import-"
            f"{provider_code}-"
            f"{training_type}"
        )

        configuration_json = {
            "lineage": {
                "source": (
                    "pre_versioned_"
                    "training_job"
                ),
                "configuration_captured": (
                    False
                ),
                "provider_id": provider_id,
                "provider_code": (
                    provider_code
                ),
                "original_runtime_class": (
                    runtime_class
                ),
            }
        }

        configuration_id = (
            connection.execute(
                sa.text(
                    """
                    INSERT INTO
                        training_configurations
                    (
                        configuration_code,
                        version,
                        training_type,
                        runtime_code,
                        configuration_json,
                        is_active,
                        created_at,
                        updated_at
                    )
                    VALUES
                    (
                        :configuration_code,
                        1,
                        :training_type,
                        :runtime_code,
                        CAST(
                            :configuration_json
                            AS jsonb
                        ),
                        FALSE,
                        NOW(),
                        NOW()
                    )
                    RETURNING id
                    """
                ),
                {
                    "configuration_code": (
                        configuration_code
                    ),
                    "training_type": (
                        training_type
                    ),
                    "runtime_code": (
                        "LEGACY_UNCONFIGURED"
                    ),
                    "configuration_json": (
                        __import__(
                            "json"
                        ).dumps(
                            configuration_json
                        )
                    ),
                },
            ).scalar_one()
        )

        connection.execute(
            sa.text(
                """
                UPDATE training_jobs
                SET training_configuration_id =
                    :configuration_id
                WHERE training_provider_id =
                    :provider_id
                  AND training_type =
                    :training_type
                  AND training_configuration_id
                    IS NULL
                """
            ),
            {
                "configuration_id": (
                    configuration_id
                ),
                "provider_id": (
                    provider_id
                ),
                "training_type": (
                    training_type
                ),
            },
        )

    remaining_null_count = (
        connection.execute(
            sa.text(
                """
                SELECT COUNT(*)
                FROM training_jobs
                WHERE training_configuration_id
                    IS NULL
                """
            )
        ).scalar_one()
    )

    if remaining_null_count != 0:

        raise RuntimeError(
            "Training configuration backfill "
            "did not cover every training job."
        )

    op.alter_column(
        "training_jobs",
        "training_configuration_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        op.f(
            "ix_training_jobs_"
            "training_configuration_id"
        ),
        "training_jobs",
        ["training_configuration_id"],
        unique=False,
    )

    op.create_foreign_key(
        (
            "fk_training_job_"
            "training_configuration_id"
        ),
        "training_jobs",
        "training_configurations",
        ["training_configuration_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:

    op.drop_constraint(
        (
            "fk_training_job_"
            "training_configuration_id"
        ),
        "training_jobs",
        type_="foreignkey",
    )

    op.drop_index(
        op.f(
            "ix_training_jobs_"
            "training_configuration_id"
        ),
        table_name="training_jobs",
    )

    op.drop_column(
        "training_jobs",
        "training_configuration_id",
    )

    op.drop_index(
        op.f(
            "ix_training_configurations_"
            "training_type"
        ),
        table_name="training_configurations",
    )

    op.drop_index(
        op.f(
            "ix_training_configurations_"
            "runtime_code"
        ),
        table_name="training_configurations",
    )

    op.drop_index(
        op.f(
            "ix_training_configurations_"
            "is_active"
        ),
        table_name="training_configurations",
    )

    op.drop_index(
        op.f(
            "ix_training_configurations_id"
        ),
        table_name="training_configurations",
    )

    op.drop_index(
        op.f(
            "ix_training_configurations_"
            "configuration_code"
        ),
        table_name="training_configurations",
    )

    op.drop_table(
        "training_configurations"
    )