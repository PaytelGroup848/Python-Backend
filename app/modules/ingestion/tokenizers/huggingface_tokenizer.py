from app.shared.factories.tokenizer_factory import (
    tokenizer_factory
)

from app.modules.ingestion.tokenizers.base_tokenizer import (
    BaseTokenizer
)


class HuggingFaceTokenizer(
    BaseTokenizer
):

    @property
    def tokenizer_code(
        self
    ) -> str:

        return "HUGGINGFACE"

    async def count_tokens(
        self,
        text: str,
        configuration: dict
    ) -> int:

        tokenizer = (
            tokenizer_factory.get_huggingface_tokenizer(

                model_name=configuration[
                    "model_name"
                ],

                trust_remote_code=configuration[
                    "trust_remote_code"
                ]

            )
        )

        tokens = tokenizer.encode(

            text,

            add_special_tokens=configuration[
                "add_special_tokens"
            ]

        )

        return len(
            tokens
        )


huggingface_tokenizer = (
    HuggingFaceTokenizer()
)