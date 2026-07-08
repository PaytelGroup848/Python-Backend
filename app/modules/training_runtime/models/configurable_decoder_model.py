import math

import torch

from torch import (
    nn,
)

from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)


class ConfigurableDecoderModel(
    TrainableModel
):

    def __init__(
        self,
        configuration: dict,
    ):

        super().__init__()

        self.vocab_size = self._positive_int(
            configuration,
            "vocab_size",
        )

        self.hidden_size = self._positive_int(
            configuration,
            "hidden_size",
        )

        self.num_layers = self._positive_int(
            configuration,
            "num_layers",
        )

        self.num_attention_heads = self._positive_int(
            configuration,
            "num_attention_heads",
        )

        self.intermediate_size = self._positive_int(
            configuration,
            "intermediate_size",
        )

        self.max_sequence_length = self._positive_int(
            configuration,
            "max_sequence_length",
        )

        if (
            self.hidden_size
            %
            self.num_attention_heads
            != 0
        ):
            raise ValueError(
                "'hidden_size' must be divisible by "
                "'num_attention_heads'."
            )

        dropout = self._probability(
            configuration,
            "dropout",
        )

        activation = self._required_string(
            configuration,
            "activation",
        )

        norm_first = self._required_bool(
            configuration,
            "norm_first",
        )

        linear_bias = self._required_bool(
            configuration,
            "linear_bias",
        )

        embedding_scale = self._required_bool(
            configuration,
            "embedding_scale",
        )

        initialization_std = self._positive_number(
            configuration,
            "initialization_std",
        )

        self._embedding_scale = (
            math.sqrt(
                self.hidden_size
            )
            if embedding_scale
            else 1.0
        )

        self.token_embedding = nn.Embedding(
            num_embeddings=self.vocab_size,
            embedding_dim=self.hidden_size,
        )

        self.position_embedding = nn.Embedding(
            num_embeddings=(
                self.max_sequence_length
            ),
            embedding_dim=self.hidden_size,
        )

        decoder_layer = nn.TransformerEncoderLayer(
            d_model=self.hidden_size,
            nhead=self.num_attention_heads,
            dim_feedforward=self.intermediate_size,
            dropout=dropout,
            activation=activation,
            batch_first=True,
            norm_first=norm_first,
            bias=linear_bias,
        )

        self.decoder = nn.TransformerEncoder(
            encoder_layer=decoder_layer,
            num_layers=self.num_layers,
        )

        self.final_norm = nn.LayerNorm(
            normalized_shape=self.hidden_size,
        )

        self.output_projection = nn.Linear(
            in_features=self.hidden_size,
            out_features=self.vocab_size,
            bias=linear_bias,
        )

        self._initialize_parameters(
            initialization_std=(
                initialization_std
            ),
        )


    @staticmethod
    def _positive_int(
        configuration: dict,
        key: str,
    ) -> int:

        value = configuration.get(
            key
        )

        if (
            isinstance(value, bool)
            or
            not isinstance(value, int)
            or
            value <= 0
        ):
            raise ValueError(
                f"'{key}' must be a positive integer."
            )

        return value


    @staticmethod
    def _positive_number(
        configuration: dict,
        key: str,
    ) -> float:

        value = configuration.get(
            key
        )

        if (
            isinstance(value, bool)
            or
            not isinstance(
                value,
                (int, float),
            )
            or
            value <= 0
        ):
            raise ValueError(
                f"'{key}' must be positive."
            )

        return float(
            value
        )


    @staticmethod
    def _probability(
        configuration: dict,
        key: str,
    ) -> float:

        value = configuration.get(
            key
        )

        if (
            isinstance(value, bool)
            or
            not isinstance(
                value,
                (int, float),
            )
            or
            value < 0
            or
            value >= 1
        ):
            raise ValueError(
                f"'{key}' must be in [0, 1)."
            )

        return float(
            value
        )


    @staticmethod
    def _required_string(
        configuration: dict,
        key: str,
    ) -> str:

        value = configuration.get(
            key
        )

        if (
            not isinstance(value, str)
            or
            not value.strip()
        ):
            raise ValueError(
                f"'{key}' must be a non-empty string."
            )

        return value.strip()


    @staticmethod
    def _required_bool(
        configuration: dict,
        key: str,
    ) -> bool:

        value = configuration.get(
            key
        )

        if not isinstance(
            value,
            bool,
        ):
            raise ValueError(
                f"'{key}' must be a boolean."
            )

        return value


    def _initialize_parameters(
        self,
        initialization_std: float,
    ) -> None:

        for module in self.modules():

            if isinstance(
                module,
                nn.Linear,
            ):

                nn.init.normal_(
                    module.weight,
                    mean=0.0,
                    std=initialization_std,
                )

                if module.bias is not None:
                    nn.init.zeros_(
                        module.bias
                    )

            elif isinstance(
                module,
                nn.Embedding,
            ):

                nn.init.normal_(
                    module.weight,
                    mean=0.0,
                    std=initialization_std,
                )


    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:

        if input_ids.ndim != 2:
            raise ValueError(
                "'input_ids' must have shape "
                "[batch_size, sequence_length]."
            )

        batch_size, sequence_length = (
            input_ids.shape
        )

        if (
            sequence_length
            >
            self.max_sequence_length
        ):
            raise ValueError(
                "Input sequence exceeds configured "
                "maximum sequence length."
            )

        positions = torch.arange(
            sequence_length,
            device=input_ids.device,
        )

        positions = (
            positions
            .unsqueeze(0)
            .expand(
                batch_size,
                sequence_length,
            )
        )

        hidden_states = (
            self.token_embedding(
                input_ids
            )
            *
            self._embedding_scale
        )

        hidden_states = (
            hidden_states
            +
            self.position_embedding(
                positions
            )
        )

        causal_mask = torch.triu(
            torch.ones(
                (
                    sequence_length,
                    sequence_length,
                ),
                device=input_ids.device,
                dtype=torch.bool,
            ),
            diagonal=1,
        )

        padding_mask = None

        if attention_mask is not None:

            if (
                attention_mask.shape
                !=
                input_ids.shape
            ):
                raise ValueError(
                    "'attention_mask' shape must match "
                    "'input_ids'."
                )

            padding_mask = (
                attention_mask == 0
            )

        hidden_states = self.decoder(
            hidden_states,
            mask=causal_mask,
            src_key_padding_mask=(
                padding_mask
            ),
        )

        hidden_states = self.final_norm(
            hidden_states
        )

        return self.output_projection(
            hidden_states
        )