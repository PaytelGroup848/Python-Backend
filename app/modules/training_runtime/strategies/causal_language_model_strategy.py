import contextlib

import torch

from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)

from app.modules.training_runtime.contracts.training_strategy import (
    TrainingStrategy,
)

from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)

from app.modules.training_runtime.schemas.tokenized_training_sample import (
    TokenizedTrainingSample,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)


class CausalLanguageModelStrategy(
    TrainingStrategy
):

    async def initialize(
        self,
        runtime: TrainingRuntime,
        model: TrainableModel,
        configuration: dict,
    ) -> dict:

        execution = configuration.get(
            "execution"
        )

        if not isinstance(execution, dict):
            raise ValueError(
                "Training strategy must define "
                "'execution' as an object."
            )

        device_name = execution.get(
            "device"
        )

        if (
            not isinstance(device_name, str)
            or
            not device_name.strip()
        ):
            raise ValueError(
                "Execution configuration must define "
                "'device'."
            )

        device = torch.device(
            device_name.strip()
        )

        if (
            device.type == "cuda"
            and
            not torch.cuda.is_available()
        ):
            raise RuntimeError(
                "Configured CUDA execution is unavailable."
            )

        precision = execution.get(
            "precision"
        )

        if (
            not isinstance(precision, str)
            or
            not precision.strip()
        ):
            raise ValueError(
                "Execution configuration must define "
                "'precision'."
            )

        precision = (
            precision.strip().lower()
        )

        precision_dtypes = {
            "fp32": torch.float32,
            "fp16": torch.float16,
            "bf16": torch.bfloat16,
        }

        if precision not in precision_dtypes:
            raise ValueError(
                "Unsupported configured precision."
            )

        if (
            precision == "bf16"
            and
            device.type == "cuda"
            and
            not torch.cuda.is_bf16_supported()
        ):
            raise RuntimeError(
                "Configured BF16 execution is unavailable."
            )

        gradient_accumulation_steps = (
            execution.get(
                "gradient_accumulation_steps"
            )
        )

        if (
            isinstance(
                gradient_accumulation_steps,
                bool,
            )
            or
            not isinstance(
                gradient_accumulation_steps,
                int,
            )
            or
            gradient_accumulation_steps <= 0
        ):
            raise ValueError(
                "'gradient_accumulation_steps' must "
                "be a positive integer."
            )

        max_grad_norm = execution.get(
            "max_grad_norm"
        )

        if (
            max_grad_norm is not None
            and
            (
                isinstance(max_grad_norm, bool)
                or
                not isinstance(
                    max_grad_norm,
                    (int, float),
                )
                or
                max_grad_norm <= 0
            )
        ):
            raise ValueError(
                "'max_grad_norm' must be positive "
                "when configured."
            )

        optimizer_configuration = (
            configuration.get(
                "optimizer"
            )
        )

        if not isinstance(
            optimizer_configuration,
            dict,
        ):
            raise ValueError(
                "Training strategy must define "
                "'optimizer' as an object."
            )

        optimizer_class_path = (
            optimizer_configuration.get(
                "class_path"
            )
        )

        if (
            not isinstance(
                optimizer_class_path,
                str,
            )
            or
            not optimizer_class_path.strip()
        ):
            raise ValueError(
                "Optimizer configuration must define "
                "'class_path'."
            )

        optimizer_kwargs = (
            optimizer_configuration.get(
                "kwargs",
                {},
            )
        )

        if not isinstance(
            optimizer_kwargs,
            dict,
        ):
            raise ValueError(
                "Optimizer 'kwargs' must be an object."
            )

        model.to(
            device=device
        )

        trainable_parameters = [
            parameter
            for parameter in model.parameters()
            if parameter.requires_grad
        ]

        if not trainable_parameters:
            raise ValueError(
                "Trainable model has no parameters "
                "with requires_grad=True."
            )

        optimizer_class = (
            dynamic_class_resolver
            .resolve_class(
                class_path=(
                    optimizer_class_path.strip()
                ),
                expected_base_class=(
                    torch.optim.Optimizer
                ),
            )
        )

        optimizer = optimizer_class(
            trainable_parameters,
            **optimizer_kwargs,
        )

        loss_configuration = (
            configuration.get(
                "loss"
            )
        )

        if not isinstance(
            loss_configuration,
            dict,
        ):
            raise ValueError(
                "Training strategy must define "
                "'loss' as an object."
            )

        loss_class_path = (
            loss_configuration.get(
                "class_path"
            )
        )

        if (
            not isinstance(
                loss_class_path,
                str,
            )
            or
            not loss_class_path.strip()
        ):
            raise ValueError(
                "Loss configuration must define "
                "'class_path'."
            )

        loss_kwargs = (
            loss_configuration.get(
                "kwargs",
                {},
            )
        )

        if not isinstance(
            loss_kwargs,
            dict,
        ):
            raise ValueError(
                "Loss 'kwargs' must be an object."
            )

        loss_class = (
            dynamic_class_resolver
            .resolve_class(
                class_path=(
                    loss_class_path.strip()
                ),
                expected_base_class=(
                    torch.nn.Module
                ),
            )
        )

        loss_function = loss_class(
            **loss_kwargs
        ).to(
            device=device
        )

        scheduler = None

        scheduler_configuration = (
            configuration.get(
                "scheduler"
            )
        )

        if scheduler_configuration is not None:

            if not isinstance(
                scheduler_configuration,
                dict,
            ):
                raise ValueError(
                    "'scheduler' must be an object."
                )

            scheduler_class_path = (
                scheduler_configuration.get(
                    "class_path"
                )
            )

            if (
                not isinstance(
                    scheduler_class_path,
                    str,
                )
                or
                not scheduler_class_path.strip()
            ):
                raise ValueError(
                    "Scheduler configuration must define "
                    "'class_path'."
                )

            scheduler_kwargs = (
                scheduler_configuration.get(
                    "kwargs",
                    {},
                )
            )

            if not isinstance(
                scheduler_kwargs,
                dict,
            ):
                raise ValueError(
                    "Scheduler 'kwargs' must be an object."
                )

            scheduler_class = (
                dynamic_class_resolver
                .resolve_class(
                    class_path=(
                        scheduler_class_path.strip()
                    ),
                )
            )

            scheduler = scheduler_class(
                optimizer,
                **scheduler_kwargs,
            )

        scaler = None

        if (
            device.type == "cuda"
            and
            precision == "fp16"
        ):
            scaler = torch.amp.GradScaler(
                "cuda"
            )

        optimizer.zero_grad(
            set_to_none=True
        )

        return {
            "optimizer": optimizer,
            "loss_function": loss_function,
            "scheduler": scheduler,
            "scaler": scaler,
            "device": device,
            "precision": precision,
            "precision_dtype": (
                precision_dtypes[
                    precision
                ]
            ),
            "gradient_accumulation_steps": (
                gradient_accumulation_steps
            ),
            "max_grad_norm": (
                float(max_grad_norm)
                if max_grad_norm is not None
                else None
            ),
            "micro_step_count": 0,
            "step_count": 0,
            "trainable_parameter_count": sum(
                parameter.numel()
                for parameter in trainable_parameters
            ),
        }


    async def train_batch(
        self,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_state: object,
        samples: list[
            TokenizedTrainingSample
        ],
        configuration: dict,
    ) -> dict:

        if not isinstance(
            strategy_state,
            dict,
        ):
            raise ValueError(
                "Strategy state is invalid."
            )

        if not samples:
            return {
                "loss": 0.0,
                "sample_count": 0,
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
                "optimizer_step_performed": False,
            }

        sequence_lengths = {
            len(sample.input_ids)
            for sample in samples
        }

        if len(sequence_lengths) != 1:
            raise ValueError(
                "Tokenized samples in a training batch "
                "must have equal sequence lengths."
            )

        device = strategy_state[
            "device"
        ]

        input_ids = torch.tensor(
            [
                sample.input_ids
                for sample in samples
            ],
            dtype=torch.long,
            device=device,
        )

        attention_mask = torch.tensor(
            [
                sample.attention_mask
                for sample in samples
            ],
            dtype=torch.long,
            device=device,
        )

        labels = torch.tensor(
            [
                sample.labels
                for sample in samples
            ],
            dtype=torch.long,
            device=device,
        )

        optimizer = strategy_state[
            "optimizer"
        ]

        loss_function = strategy_state[
            "loss_function"
        ]

        scheduler = strategy_state[
            "scheduler"
        ]

        scaler = strategy_state[
            "scaler"
        ]

        accumulation_steps = (
            strategy_state[
                "gradient_accumulation_steps"
            ]
        )

        model.train()

        precision = strategy_state[
            "precision"
        ]

        autocast_enabled = (
            device.type == "cuda"
            and
            precision in {
                "fp16",
                "bf16",
            }
        )

        autocast_context = (
            torch.autocast(
                device_type=device.type,
                dtype=(
                    strategy_state[
                        "precision_dtype"
                    ]
                ),
                enabled=True,
            )
            if autocast_enabled
            else contextlib.nullcontext()
        )

        with autocast_context:

            logits = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )

            if logits.ndim != 3:
                raise ValueError(
                    "Trainable model must return logits "
                    "with shape [batch, sequence, vocabulary]."
                )

            shifted_logits = (
                logits[:, :-1, :]
                .contiguous()
            )

            shifted_labels = (
                labels[:, 1:]
                .contiguous()
            )

            raw_loss = loss_function(
                shifted_logits.view(
                    -1,
                    shifted_logits.size(-1),
                ),
                shifted_labels.view(-1),
            )

            loss = (
                raw_loss
                /
                accumulation_steps
            )

        if scaler is not None:
            scaler.scale(
                loss
            ).backward()
        else:
            loss.backward()

        strategy_state[
            "micro_step_count"
        ] += 1

        optimizer_step_performed = (
            strategy_state[
                "micro_step_count"
            ]
            %
            accumulation_steps
            ==
            0
        )

        if optimizer_step_performed:
            self._perform_optimizer_step(
                model=model,
                strategy_state=strategy_state,
            )

        return {
            "loss": float(
                raw_loss
                .detach()
                .float()
                .cpu()
                .item()
            ),
            "sample_count": len(
                samples
            ),
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
            "optimizer_step_performed": (
                optimizer_step_performed
            ),
            "device": str(
                device
            ),
            "precision": precision,
        }


    async def finalize(
        self,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_state: object,
        configuration: dict,
    ) -> dict:

        if not isinstance(
            strategy_state,
            dict,
        ):
            raise ValueError(
                "Strategy state is invalid."
            )

        accumulation_steps = (
            strategy_state[
                "gradient_accumulation_steps"
            ]
        )

        pending_micro_steps = (
            strategy_state[
                "micro_step_count"
            ]
            %
            accumulation_steps
        )

        final_optimizer_step_performed = False

        if pending_micro_steps:
            self._perform_optimizer_step(
                model=model,
                strategy_state=strategy_state,
            )

            final_optimizer_step_performed = True

        device = strategy_state[
            "device"
        ]

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
            "trainable_parameter_count": (
                strategy_state[
                    "trainable_parameter_count"
                ]
            ),
            "final_optimizer_step_performed": (
                final_optimizer_step_performed
            ),
            "device": str(
                device
            ),
            "precision": (
                strategy_state[
                    "precision"
                ]
            ),
            "cuda_memory_allocated": (
                torch.cuda.memory_allocated(
                    device
                )
                if device.type == "cuda"
                else 0
            ),
            "cuda_max_memory_allocated": (
                torch.cuda.max_memory_allocated(
                    device
                )
                if device.type == "cuda"
                else 0
            ),
        }


    @staticmethod
    def _perform_optimizer_step(
        model: TrainableModel,
        strategy_state: dict,
    ) -> None:

        optimizer = strategy_state[
            "optimizer"
        ]

        scheduler = strategy_state[
            "scheduler"
        ]

        scaler = strategy_state[
            "scaler"
        ]

        max_grad_norm = strategy_state[
            "max_grad_norm"
        ]

        if max_grad_norm is not None:

            if scaler is not None:
                scaler.unscale_(
                    optimizer
                )

            torch.nn.utils.clip_grad_norm_(
                (
                    parameter
                    for parameter in model.parameters()
                    if parameter.requires_grad
                ),
                max_norm=max_grad_norm,
            )

        if scaler is not None:
            scaler.step(
                optimizer
            )
            scaler.update()
        else:
            optimizer.step()

        if scheduler is not None:
            scheduler.step()

        optimizer.zero_grad(
            set_to_none=True
        )

        strategy_state[
            "step_count"
        ] += 1