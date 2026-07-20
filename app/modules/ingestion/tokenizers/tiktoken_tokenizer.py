
from app.modules.ingestion.tokenizers.base_tokenizer import (
    BaseTokenizer
)

from app.shared.factories.tokenizer_factory import (
    tokenizer_factory
)


class TikTokenTokenizer(
    BaseTokenizer
):

    @property
    def tokenizer_code(
        self
    ) -> str:

        return "TIKTOKEN"

    async def count_tokens(
        self,
        text: str,
        configuration: dict
    ) -> int:

        tokenizer = (
            tokenizer_factory.get_tiktoken_tokenizer(

                encoding_name=configuration[
                    "encoding_name"
                ]

            )
        )

        tokens = tokenizer.encode(
            text
        )

        return len(
            tokens
        )


tiktoken_tokenizer = (
    TikTokenTokenizer()
)