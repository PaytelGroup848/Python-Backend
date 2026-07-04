from abc import (
    ABC,
    abstractmethod
)


class BaseConnectorRuntime(
    ABC
):

    @abstractmethod
    async def execute(
        self,
        configuration: dict
    ) -> dict:

        raise NotImplementedError