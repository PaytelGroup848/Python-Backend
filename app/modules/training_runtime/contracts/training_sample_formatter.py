from abc import (
    ABC,
    abstractmethod,
)

from app.modules.training_runtime.schemas.training_data_record import (
    TrainingDataRecord,
)

from app.modules.training_runtime.schemas.formatted_training_sample import (
    FormattedTrainingSample,
)


class TrainingSampleFormatter(
    ABC
):

    @abstractmethod
    def format_record(
        self,
        record: TrainingDataRecord,
        configuration: dict,
    ) -> FormattedTrainingSample:
        raise NotImplementedError