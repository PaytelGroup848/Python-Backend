from typing import Any
from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        messages: list | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        tools: list | None = None,
        metadata: dict | None = None,
    ) -> Any:
        pass

    @abstractmethod
    async def health_check(
        self,
    ) -> Any:
        pass