from app.modules.ingestion.schemas.nlp_document import (
    NLPDocument
)

from app.modules.ingestion.registry.nlp_registry import (
    nlp_registry
)

from app.modules.pipeline_runtime.schemas.base_provider_configuration import (
    BaseProviderConfiguration
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class NLPExecutionService:

    async def parse(
        self,
        text: str,
        provider_code: str,
        configuration: BaseProviderConfiguration
    ) -> NLPDocument:

        provider = nlp_registry.get_provider(
            provider_code
        )

        document = await provider.parse(
            text=text,
            configuration=configuration
        )

        if not isinstance(
            document,
            NLPDocument
        ):

            raise BusinessException(
                "NLP provider returned an invalid document."
            )

        return document


nlp_execution_service = (
    NLPExecutionService()
)