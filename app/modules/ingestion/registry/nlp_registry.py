from app.modules.ingestion.nlp.base_nlp_provider import (
    BaseNLPProvider
)

from app.shared.exceptions.business_exception import (
    BusinessException
)
from app.modules.ingestion.nlp.spacy_provider import (
    spacy_provider
)


class NLPRegistry:

    def __init__(
        self
    ):

        self._providers: dict[
            str,
            BaseNLPProvider
        ] = {}

        self.register(
            spacy_provider
        )

    def register(
        self,
        provider: BaseNLPProvider
    ) -> None:

        provider_code = (
            provider.provider_code.upper()
        )

        if provider_code in self._providers:

            raise BusinessException(

                f"NLP provider '{provider_code}' is already registered."

            )

        self._providers[
            provider_code
        ] = provider

    def get_provider(
        self,
        provider_code: str
    ) -> BaseNLPProvider:

        provider = self._providers.get(
            provider_code.upper()
        )

        if provider is None:

            raise BusinessException(

                f"NLP provider '{provider_code}' is not registered."

            )

        return provider

    @property
    def providers(
        self
    ) -> dict[
        str,
        BaseNLPProvider
    ]:

        return self._providers.copy()


nlp_registry = NLPRegistry()