from app.modules.training_runtime.contracts.training_sample_formatter import (
    TrainingSampleFormatter,
)

from app.modules.training_runtime.formatters.prompt_completion_formatter import (
    PromptCompletionFormatter,
)


class TrainingSampleFormatterFactory:

    def __init__(
        self,
    ):

        self._registry: dict[
            str,
            TrainingSampleFormatter,
        ] = {}

        self.register(
            formatter_code=(
                PromptCompletionFormatter
                .FORMATTER_CODE
            ),
            formatter=(
                PromptCompletionFormatter()
            ),
        )

    def register(
        self,
        formatter_code: str,
        formatter: TrainingSampleFormatter,
    ) -> None:

        normalized_code = (
            formatter_code
            .strip()
            .upper()
        )

        if not normalized_code:
            raise ValueError(
                "Formatter code cannot be empty."
            )

        self._registry[
            normalized_code
        ] = formatter

    def get_formatter(
        self,
        formatter_code: str,
    ) -> TrainingSampleFormatter:

        normalized_code = (
            formatter_code
            .strip()
            .upper()
        )

        formatter = (
            self._registry
            .get(
                normalized_code
            )
        )

        if formatter is None:
            raise ValueError(
                f"Training sample formatter "
                f"'{formatter_code}' "
                f"is not registered."
            )

        return formatter


training_sample_formatter_factory = (
    TrainingSampleFormatterFactory()
)