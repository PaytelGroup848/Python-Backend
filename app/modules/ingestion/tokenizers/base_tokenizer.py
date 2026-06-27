from abc import (
    ABC,
    abstractmethod
)


class BaseTokenizer(
    ABC
):

    @property
    @abstractmethod
    def tokenizer_code(
        self
    ) -> str:
        """
        Unique tokenizer identifier.

        Examples:
            TIKTOKEN
            HUGGINGFACE
            SENTENCEPIECE
        """
        raise NotImplementedError

    @abstractmethod
    async def count_tokens(
        self,
        text: str,
        configuration: dict
    ) -> int:
        """
        Return the number of tokens for the supplied text.
        """
        raise NotImplementedError