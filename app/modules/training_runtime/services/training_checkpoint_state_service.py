import io
import random

import torch

from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)


class TrainingCheckpointStateService:

    FORMAT_VERSION = 1

    def serialize(
        self,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_state: dict,
        data_cursor: dict,
    ) -> bytes:

        if not isinstance(strategy_state, dict):
            raise ValueError(
                "Strategy state must be an object."
            )

        if not isinstance(data_cursor, dict):
            raise ValueError(
                "Data cursor must be an object."
            )

        optimizer = strategy_state.get(
            "optimizer"
        )

        if optimizer is None:
            raise ValueError(
                "Strategy state has no optimizer."
            )

        scheduler = strategy_state.get(
            "scheduler"
        )

        scaler = strategy_state.get(
            "scaler"
        )

        payload = {
            "format_version": self.FORMAT_VERSION,

            "lineage": {
                "training_job_id": (
                    runtime.training_job_id
                ),
                "dataset_id": (
                    runtime.dataset_id
                ),
                "dataset_snapshot_id": (
                    runtime.dataset_snapshot_id
                ),
                "snapshot_content_hash": (
                    runtime.snapshot_content_hash
                ),
                "base_model_id": (
                    runtime.base_model_id
                ),
                "base_model_version_id": (
                    runtime.base_model_version_id
                ),
                "tokenizer_version_id": (
                    runtime.tokenizer_version_id
                ),
                "tokenizer_content_hash": (
                    runtime.tokenizer_content_hash
                ),
                "training_configuration_id": (
                    runtime.training_configuration_id
                ),
            },

            "progress": {
                "step_count": int(
                    strategy_state.get(
                        "step_count",
                        0,
                    )
                ),
                "micro_step_count": int(
                    strategy_state.get(
                        "micro_step_count",
                        0,
                    )
                ),
                "data_cursor": dict(
                    data_cursor
                ),
            },

            "model_state_dict": (
                model.state_dict()
            ),

            "optimizer_state_dict": (
                optimizer.state_dict()
            ),

            "scheduler_state_dict": (
                scheduler.state_dict()
                if scheduler is not None
                else None
            ),

            "scaler_state_dict": (
                scaler.state_dict()
                if scaler is not None
                else None
            ),

            "rng_state": {
                "python": random.getstate(),

                "torch_cpu": (
                    torch.get_rng_state()
                ),

                "torch_cuda": (
                    torch.cuda.get_rng_state_all()
                    if torch.cuda.is_available()
                    else None
                ),
            },
        }

        buffer = io.BytesIO()

        torch.save(
            payload,
            buffer,
        )

        return buffer.getvalue()


    def restore(
        self,
        payload_bytes: bytes,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_state: dict,
    ) -> dict:

        if not payload_bytes:
            raise ValueError(
                "Checkpoint payload is empty."
            )

        payload = torch.load(
            io.BytesIO(
                payload_bytes
            ),
            map_location="cpu",
            weights_only=False,
        )

        if not isinstance(payload, dict):
            raise ValueError(
                "Checkpoint payload is invalid."
            )

        if (
            payload.get("format_version")
            !=
            self.FORMAT_VERSION
        ):
            raise ValueError(
                "Unsupported checkpoint format."
            )

        lineage = payload.get(
            "lineage"
        )

        if not isinstance(lineage, dict):
            raise ValueError(
                "Checkpoint lineage is missing."
            )

        expected = {
            "training_job_id": (
                runtime.training_job_id
            ),
            "dataset_id": (
                runtime.dataset_id
            ),
            "dataset_snapshot_id": (
                runtime.dataset_snapshot_id
            ),
            "snapshot_content_hash": (
                runtime.snapshot_content_hash
            ),
            "base_model_id": (
                runtime.base_model_id
            ),
            "base_model_version_id": (
                runtime.base_model_version_id
            ),
            "tokenizer_version_id": (
                runtime.tokenizer_version_id
            ),
            "tokenizer_content_hash": (
                runtime.tokenizer_content_hash
            ),
            "training_configuration_id": (
                runtime.training_configuration_id
            ),
        }

        for key, expected_value in expected.items():

            if lineage.get(key) != expected_value:
                raise ValueError(
                    "Checkpoint lineage mismatch: "
                    + key
                )

        model.load_state_dict(
            payload[
                "model_state_dict"
            ]
        )

        optimizer = strategy_state.get(
            "optimizer"
        )

        if optimizer is None:
            raise ValueError(
                "Strategy state has no optimizer."
            )

        optimizer.load_state_dict(
            payload[
                "optimizer_state_dict"
            ]
        )

        scheduler = strategy_state.get(
            "scheduler"
        )

        scheduler_state = payload.get(
            "scheduler_state_dict"
        )

        if (
            scheduler is not None
            and
            scheduler_state is not None
        ):
            scheduler.load_state_dict(
                scheduler_state
            )

        scaler = strategy_state.get(
            "scaler"
        )

        scaler_state = payload.get(
            "scaler_state_dict"
        )

        if (
            scaler is not None
            and
            scaler_state is not None
        ):
            scaler.load_state_dict(
                scaler_state
            )

        progress = payload.get(
            "progress"
        )

        if not isinstance(progress, dict):
            raise ValueError(
                "Checkpoint progress is missing."
            )

        strategy_state[
            "step_count"
        ] = int(
            progress.get(
                "step_count",
                0,
            )
        )

        strategy_state[
            "micro_step_count"
        ] = int(
            progress.get(
                "micro_step_count",
                0,
            )
        )

        rng_state = payload.get(
            "rng_state",
            {},
        )

        python_state = rng_state.get(
            "python"
        )

        if python_state is not None:
            random.setstate(
                python_state
            )

        cpu_state = rng_state.get(
            "torch_cpu"
        )

        if cpu_state is not None:
            torch.set_rng_state(
                cpu_state
            )

        cuda_state = rng_state.get(
            "torch_cuda"
        )

        if (
            cuda_state is not None
            and
            torch.cuda.is_available()
        ):
            torch.cuda.set_rng_state_all(
                cuda_state
            )

        data_cursor = progress.get(
            "data_cursor",
            {},
        )

        if not isinstance(data_cursor, dict):
            raise ValueError(
                "Checkpoint data cursor is invalid."
            )

        return {
            "step_count": (
                strategy_state[
                    "step_count"
                ]
            ),
            "micro_step_count": (
                strategy_state[
                    "micro_step_count"
                ]
            ),
            "data_cursor": data_cursor,
        }


training_checkpoint_state_service = (
    TrainingCheckpointStateService()
)