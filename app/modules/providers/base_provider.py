from abc import ABC
from abc import abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        model: str | None = None,
        messages: list | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        tools: list | None = None,
        metadata: dict | None = None,
    ):
        pass

    @abstractmethod
    async def health_check(
        self,
    ):
        pass