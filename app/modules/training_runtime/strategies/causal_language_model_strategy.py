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
            model.parameters(),
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
        )

        return {
            "optimizer": optimizer,
            "loss_function": loss_function,
            "step_count": 0,
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

        for sample in samples:

            if (
                len(sample.attention_mask)
                !=
                len(sample.input_ids)
            ):
                raise ValueError(
                    "Attention mask length does not match "
                    "input IDs length."
                )

            if (
                len(sample.labels)
                !=
                len(sample.input_ids)
            ):
                raise ValueError(
                    "Labels length does not match "
                    "input IDs length."
                )

        input_ids = torch.tensor(
            [
                sample.input_ids
                for sample in samples
            ],
            dtype=torch.long,
        )

        attention_mask = torch.tensor(
            [
                sample.attention_mask
                for sample in samples
            ],
            dtype=torch.long,
        )

        labels = torch.tensor(
            [
                sample.labels
                for sample in samples
            ],
            dtype=torch.long,
        )

        optimizer = (
            strategy_state["optimizer"]
        )

        loss_function = (
            strategy_state["loss_function"]
        )

        model.train()

        optimizer.zero_grad()

        logits = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )

        if logits.ndim != 3:
            raise ValueError(
                "Trainable model must return logits with "
                "shape [batch, sequence, vocabulary]."
            )

        shifted_logits = (
            logits[:, :-1, :]
            .contiguous()
        )

        shifted_labels = (
            labels[:, 1:]
            .contiguous()
        )

        loss = loss_function(
            shifted_logits.view(
                -1,
                shifted_logits.size(-1),
            ),
            shifted_labels.view(-1),
        )

        loss.backward()

        optimizer.step()

        strategy_state["step_count"] += 1

        return {
            "loss": float(
                loss.detach().cpu().item()
            ),
            "sample_count": len(samples),
            "step_count": (
                strategy_state["step_count"]
            ),
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

        return {
            "step_count": (
                strategy_state["step_count"]
            ),
        }