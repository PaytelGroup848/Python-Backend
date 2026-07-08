from abc import (
    ABC,
    abstractmethod,
)

from app.modules.training_runtime.schemas.formatted_training_sample import (
    FormattedTrainingSample,
)

from app.modules.training_runtime.schemas.tokenized_training_sample import (
    TokenizedTrainingSample,
)


class TrainingTokenizer(
    ABC
):

    @abstractmethod
    def tokenize_batch(
        self,
        samples: list[
            FormattedTrainingSample
        ],
        configuration: dict,
    ) -> list[
        TokenizedTrainingSample
    ]:
        raise NotImplementedError