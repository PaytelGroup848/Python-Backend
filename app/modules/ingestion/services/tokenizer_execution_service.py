from app.modules.ingestion.registry.tokenizer_registry import (
    tokenizer_registry
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class TokenizerExecutionService:

    async def count_tokens(
        self,
        text: str,
        tokenizer_code: str,
        configuration: dict
    ) -> int:

        tokenizer = tokenizer_registry.get_tokenizer(
            tokenizer_code
        )

        token_count = await tokenizer.count_tokens(
            text=text,
            configuration=configuration
        )

        if not isinstance(
            token_count,
            int
        ):

            raise BusinessException(
                "Tokenizer returned an invalid token count."
            )

        if token_count < 0:

            raise BusinessException(
                "Tokenizer returned a negative token count."
            )

        return token_count


tokenizer_execution_service = (
    TokenizerExecutionService()
)