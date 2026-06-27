from app.modules.ingestion.tokenizers.base_tokenizer import (
    BaseTokenizer
)

from app.shared.exceptions.business_exception import (
    BusinessException
)
from app.modules.ingestion.tokenizers.huggingface_tokenizer import (
    huggingface_tokenizer
)
from app.modules.ingestion.tokenizers.tiktoken_tokenizer import (
    tiktoken_tokenizer
)
from app.modules.ingestion.tokenizers.sentencepiece_tokenizer import (
    sentencepiece_tokenizer
)

class TokenizerRegistry:

    def __init__(
        self
    ):

        self._tokenizers: dict[
            str,
            BaseTokenizer
        ] = {}

        self.register(
            huggingface_tokenizer
        )

        self.register(
            tiktoken_tokenizer
        )

        self.register(
            sentencepiece_tokenizer
        )

    def register(
        self,
        tokenizer: BaseTokenizer
    ) -> None:

        tokenizer_code = (
            tokenizer.tokenizer_code.upper()
        )

        if tokenizer_code in self._tokenizers:

            raise BusinessException(

                f"Tokenizer '{tokenizer_code}' is already registered."

            )

        self._tokenizers[
            tokenizer_code
        ] = tokenizer

    def get_tokenizer(
        self,
        tokenizer_code: str
    ) -> BaseTokenizer:

        tokenizer = self._tokenizers.get(

            tokenizer_code.upper()

        )

        if tokenizer is None:

            raise BusinessException(

                f"Tokenizer '{tokenizer_code}' is not registered."

            )

        return tokenizer

    @property
    def tokenizers(
        self
    ) -> dict[
        str,
        BaseTokenizer
    ]:

        return self._tokenizers.copy()


tokenizer_registry = (
    TokenizerRegistry()
)