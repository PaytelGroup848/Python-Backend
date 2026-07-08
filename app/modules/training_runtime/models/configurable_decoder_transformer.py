import math

import torch

from torch import (
    nn,
)


class ConfigurableDecoderTransformer(
    nn.Module
):

    def __init__(
        self,
        configuration: dict,
    ):

        super().__init__()

        self.vocab_size = self._require_positive_int(
            configuration,
            "vocab_size",
        )

        self.hidden_size = self._require_positive_int(
            configuration,
            "hidden_size",
        )

        self.num_layers = self._require_positive_int(
            configuration,
            "num_layers",
        )

        self.num_attention_heads = self._require_positive_int(
            configuration,
            "num_attention_heads",
        )

        self.intermediate_size = self._require_positive_int(
            configuration,
            "intermediate_size",
        )

        self.max_sequence_length = self._require_positive_int(
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

        dropout = configuration.get(
            "dropout",
            0.0,
        )

        if (
            isinstance(dropout, bool)
            or
            not isinstance(
                dropout,
                (int, float),
            )
            or
            dropout < 0.0
            or
            dropout >= 1.0
        ):
            raise ValueError(
                "'dropout' must be a number in [0, 1)."
            )

        self.token_embedding = nn.Embedding(
            self.vocab_size,
            self.hidden_size,
        )

        self.position_embedding = nn.Embedding(
            self.max_sequence_length,
            self.hidden_size,
        )

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.hidden_size,
            nhead=self.num_attention_heads,
            dim_feedforward=self.intermediate_size,
            dropout=float(dropout),
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )

        self.layers = nn.TransformerEncoder(
            encoder_layer=encoder_layer,
            num_layers=self.num_layers,
        )

        self.final_norm = nn.LayerNorm(
            self.hidden_size
        )

        self.output_projection = nn.Linear(
            self.hidden_size,
            self.vocab_size,
            bias=False,
        )

        self._initialize_parameters(
            configuration
        )


    @staticmethod
    def _require_positive_int(
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


    def _initialize_parameters(
        self,
        configuration: dict,
    ) -> None:

        initialization_std = configuration.get(
            "initialization_std",
            0.02,
        )

        if (
            isinstance(initialization_std, bool)
            or
            not isinstance(
                initialization_std,
                (int, float),
            )
            or
            initialization_std <= 0
        ):
            raise ValueError(
                "'initialization_std' must be positive."
            )

        for module in self.modules():

            if isinstance(
                module,
                nn.Linear,
            ):
                nn.init.normal_(
                    module.weight,
                    mean=0.0,
                    std=float(initialization_std),
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
                    std=float(initialization_std),
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
        ).unsqueeze(0).expand(
            batch_size,
            sequence_length,
        )

        hidden_states = (
            self.token_embedding(
                input_ids
            )
            +
            self.position_embedding(
                positions
            )
        )

        causal_mask = torch.triu(
            torch.ones(
                sequence_length,
                sequence_length,
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

        hidden_states = self.layers(
            hidden_states,
            mask=causal_mask,
            src_key_padding_mask=padding_mask,
        )

        hidden_states = self.final_norm(
            hidden_states
        )

        return self.output_projection(
            hidden_states
        )