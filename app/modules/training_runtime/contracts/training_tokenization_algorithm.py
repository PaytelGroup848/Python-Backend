from abc import (
    ABC,
    abstractmethod,
)


class TrainingTokenizationAlgorithm(
    ABC
):

    @abstractmethod
    def encode(
        self,
        text: str,
        configuration: dict,
    ) -> list[int]:

        raise NotImplementedError

    @abstractmethod
    def get_special_token_id(
        self,
        token_name: str,
        configuration: dict,
    ) -> int | None:

        raise NotImplementedError