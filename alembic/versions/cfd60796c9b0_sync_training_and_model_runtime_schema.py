"""sync training and model runtime schema

Revision ID: cfd60796c9b0
Revises: fc4226062950
Create Date: 2026-07-03 05:19:58.383021
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cfd60796c9b0"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "fc4226062950"

branch_labels = None

depends_on = None


def upgrade() -> None:

    # =====================================================
    # CONNECTOR / CORPUS INDEXES
    # =====================================================

    op.create_index(
        "ix_connector_instances_id",
        "connector_instances",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_corpus_sources_id",
        "corpus_sources",
        ["id"],
        unique=False,
    )

    # =====================================================
    # DATASETS
    # Validate existing data before enforcing constraints
    # =====================================================

    connection = op.get_bind()

    null_corpus_count = connection.execute(
        sa.text("""
            SELECT COUNT(*)
            FROM datasets
            WHERE corpus_id IS NULL
        """)
    ).scalar_one()

    if null_corpus_count:

        raise RuntimeError(
            "Cannot migrate datasets: "
            f"{null_corpus_count} rows have NULL corpus_id"
        )

    duplicate_dataset_count = connection.execute(
        sa.text("""
            SELECT COUNT(*)
            FROM (
                SELECT corpus_id, version
                FROM datasets
                GROUP BY corpus_id, version
                HAVING COUNT(*) > 1
            ) AS duplicates
        """)
    ).scalar_one()

    if duplicate_dataset_count:

        raise RuntimeError(
            "Cannot create uq_dataset_corpus_version: "
            f"{duplicate_dataset_count} duplicate groups exist"
        )

    op.alter_column(
        "datasets",
        "corpus_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_unique_constraint(
        "uq_dataset_corpus_version",
        "datasets",
        [
            "corpus_id",
            "version",
        ],
    )

    # =====================================================
    # EVALUATION JOBS
    # =====================================================

    op.drop_index(
        "ix_evaluation_jobs_status",
        table_name="evaluation_jobs",
    )

    # =====================================================
    # MODEL ARTIFACTS
    # Safe server defaults for existing rows
    # =====================================================

    op.add_column(
        "model_artifacts",
        sa.Column(
            "artifact_version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
    )

    op.add_column(
        "model_artifacts",
        sa.Column(
            "storage_provider",
            sa.String(length=50),
            server_default=sa.text("'LOCAL'"),
            nullable=False,
        ),
    )

    op.add_column(
        "model_artifacts",
        sa.Column(
            "mime_type",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "model_artifacts",
        sa.Column(
            "compression",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "model_artifacts",
        sa.Column(
            "status",
            sa.String(length=50),
            server_default=sa.text("'READY'"),
            nullable=False,
        ),
    )

    op.drop_index(
        "ix_model_artifacts_artifact_type",
        table_name="model_artifacts",
    )

    # =====================================================
    # MODEL PROMOTIONS
    # =====================================================

    op.add_column(
        "model_promotions",
        sa.Column(
            "target_environment",
            sa.String(length=50),
            server_default=sa.text("'DEVELOPMENT'"),
            nullable=False,
        ),
    )

    op.add_column(
        "model_promotions",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    op.add_column(
        "model_promotions",
        sa.Column(
            "approved_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.drop_index(
        "ix_model_promotions_status",
        table_name="model_promotions",
    )

    op.create_index(
        "ix_model_promotions_promotion_status",
        "model_promotions",
        ["promotion_status"],
        unique=False,
    )

    # =====================================================
    # MODEL RELEASES
    # =====================================================

    op.add_column(
        "model_releases",
        sa.Column(
            "checksum",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "model_releases",
        sa.Column(
            "is_default",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    op.drop_index(
        "ix_model_releases_status",
        table_name="model_releases",
    )

    op.create_index(
        "ix_model_releases_release_status",
        "model_releases",
        ["release_status"],
        unique=False,
    )

    # =====================================================
    # PIPELINE INDEXES
    # =====================================================

    op.create_index(
        "ix_pipeline_runs_id",
        "pipeline_runs",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_pipeline_step_runs_id",
        "pipeline_step_runs",
        ["id"],
        unique=False,
    )

    # =====================================================
    # TRAINING JOBS
    # Safe base_model -> base_model_id migration
    # =====================================================

    op.add_column(
        "training_jobs",
        sa.Column(
            "base_model_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "training_jobs",
        sa.Column(
            "priority",
            sa.Integer(),
            server_default=sa.text("100"),
            nullable=False,
        ),
    )

    op.add_column(
        "training_jobs",
        sa.Column(
            "created_by",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "training_jobs",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    # Map legacy base_model string to models.code first.
    # If older data used display_name instead of code,
    # use that as a fallback.
    connection.execute(
        sa.text("""
            UPDATE training_jobs AS tj
            SET base_model_id = m.id
            FROM models AS m
            WHERE tj.base_model_id IS NULL
              AND tj.base_model IS NOT NULL
              AND (
                    m.code = tj.base_model
                    OR m.display_name = tj.base_model
              )
        """)
    )

    unmapped_base_models = connection.execute(
        sa.text("""
            SELECT COUNT(*)
            FROM training_jobs
            WHERE base_model_id IS NULL
        """)
    ).scalar_one()

    if unmapped_base_models:

        raise RuntimeError(
            "Cannot migrate training_jobs.base_model: "
            f"{unmapped_base_models} rows could not be mapped "
            "to models.id"
        )

    null_provider_count = connection.execute(
        sa.text("""
            SELECT COUNT(*)
            FROM training_jobs
            WHERE training_provider_id IS NULL
        """)
    ).scalar_one()

    if null_provider_count:

        raise RuntimeError(
            "Cannot make training_provider_id NOT NULL: "
            f"{null_provider_count} rows contain NULL"
        )

    op.alter_column(
        "training_jobs",
        "base_model_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "training_jobs",
        "training_provider_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        "ix_training_jobs_base_model_id",
        "training_jobs",
        ["base_model_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_training_job_base_model_id",
        "training_jobs",
        "models",
        ["base_model_id"],
        ["id"],
    )

    # Drop legacy string only after successful mapping.
    op.drop_column(
        "training_jobs",
        "base_model",
    )

    # =====================================================
    # TRAINING PROVIDERS
    # =====================================================

    op.add_column(
        "training_providers",
        sa.Column(
            "runtime_version",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "training_providers",
        sa.Column(
            "runtime_class",
            sa.String(length=500),
            server_default=sa.text("'UNCONFIGURED'"),
            nullable=False,
        ),
    )

    op.add_column(
        "training_providers",
        sa.Column(
            "capabilities",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:

    # =====================================================
    # TRAINING PROVIDERS
    # =====================================================

    op.drop_column(
        "training_providers",
        "capabilities",
    )

    op.drop_column(
        "training_providers",
        "runtime_class",
    )

    op.drop_column(
        "training_providers",
        "runtime_version",
    )

    # =====================================================
    # TRAINING JOBS
    # Restore legacy base_model safely
    # =====================================================

    op.add_column(
        "training_jobs",
        sa.Column(
            "base_model",
            sa.String(length=255),
            nullable=True,
        ),
    )

    connection = op.get_bind()

    connection.execute(
        sa.text("""
            UPDATE training_jobs AS tj
            SET base_model = m.code
            FROM models AS m
            WHERE tj.base_model_id = m.id
        """)
    )

    null_base_model_count = connection.execute(
        sa.text("""
            SELECT COUNT(*)
            FROM training_jobs
            WHERE base_model IS NULL
        """)
    ).scalar_one()

    if null_base_model_count:

        raise RuntimeError(
            "Cannot downgrade training_jobs: "
            f"{null_base_model_count} base_model values "
            "could not be restored"
        )

    op.alter_column(
        "training_jobs",
        "base_model",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.drop_constraint(
        "fk_training_job_base_model_id",
        "training_jobs",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_training_jobs_base_model_id",
        table_name="training_jobs",
    )

    op.alter_column(
        "training_jobs",
        "training_provider_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.drop_column(
        "training_jobs",
        "is_active",
    )

    op.drop_column(
        "training_jobs",
        "created_by",
    )

    op.drop_column(
        "training_jobs",
        "priority",
    )

    op.drop_column(
        "training_jobs",
        "base_model_id",
    )

    # =====================================================
    # PIPELINE INDEXES
    # =====================================================

    op.drop_index(
        "ix_pipeline_step_runs_id",
        table_name="pipeline_step_runs",
    )

    op.drop_index(
        "ix_pipeline_runs_id",
        table_name="pipeline_runs",
    )

    # =====================================================
    # MODEL RELEASES
    # =====================================================

    op.drop_index(
        "ix_model_releases_release_status",
        table_name="model_releases",
    )

    op.create_index(
        "ix_model_releases_status",
        "model_releases",
        ["release_status"],
        unique=False,
    )

    op.drop_column(
        "model_releases",
        "is_default",
    )

    op.drop_column(
        "model_releases",
        "checksum",
    )

    # =====================================================
    # MODEL PROMOTIONS
    # =====================================================

    op.drop_index(
        "ix_model_promotions_promotion_status",
        table_name="model_promotions",
    )

    op.create_index(
        "ix_model_promotions_status",
        "model_promotions",
        ["promotion_status"],
        unique=False,
    )

    op.drop_column(
        "model_promotions",
        "approved_at",
    )

    op.drop_column(
        "model_promotions",
        "is_active",
    )

    op.drop_column(
        "model_promotions",
        "target_environment",
    )

    # =====================================================
    # MODEL ARTIFACTS
    # =====================================================

    op.create_index(
        "ix_model_artifacts_artifact_type",
        "model_artifacts",
        ["artifact_type"],
        unique=False,
    )

    op.drop_column(
        "model_artifacts",
        "status",
    )

    op.drop_column(
        "model_artifacts",
        "compression",
    )

    op.drop_column(
        "model_artifacts",
        "mime_type",
    )

    op.drop_column(
        "model_artifacts",
        "storage_provider",
    )

    op.drop_column(
        "model_artifacts",
        "artifact_version",
    )

    # =====================================================
    # EVALUATION JOBS
    # =====================================================

    op.create_index(
        "ix_evaluation_jobs_status",
        "evaluation_jobs",
        ["status"],
        unique=False,
    )

    # =====================================================
    # DATASETS
    # =====================================================

    op.drop_constraint(
        "uq_dataset_corpus_version",
        "datasets",
        type_="unique",
    )

    op.alter_column(
        "datasets",
        "corpus_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # =====================================================
    # CONNECTOR / CORPUS INDEXES
    # =====================================================

    op.drop_index(
        "ix_corpus_sources_id",
        table_name="corpus_sources",
    )

    op.drop_index(
        "ix_connector_instances_id",
        table_name="connector_instances",
    )