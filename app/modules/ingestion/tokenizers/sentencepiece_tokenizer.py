
from app.modules.ingestion.tokenizers.base_tokenizer import (
    BaseTokenizer
)

from app.shared.factories.tokenizer_factory import (
    tokenizer_factory
)


class SentencePieceTokenizer(
    BaseTokenizer
):

    @property
    def tokenizer_code(
        self
    ) -> str:

        return "SENTENCEPIECE"

    async def count_tokens(
        self,
        text: str,
        configuration: dict
    ) -> int:

        tokenizer = (
            tokenizer_factory.get_sentencepiece_tokenizer(

                model_path=configuration[
                    "model_path"
                ]

            )
        )

        return len(
            tokenizer.encode(
                text
            )
        )


sentencepiece_tokenizer = (
    SentencePieceTokenizer()
)