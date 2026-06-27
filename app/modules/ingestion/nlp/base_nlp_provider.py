from abc import (
    ABC,
    abstractmethod
)

from app.modules.ingestion.schemas.nlp_document import (
    NLPDocument
)

from app.modules.pipeline_runtime.schemas.nlp_configuration import (
    NLPConfiguration
)


class BaseNLPProvider(
    ABC
):

    @property
    @abstractmethod
    def provider_code(
        self
    ) -> str:
        """
        Unique NLP provider identifier.
        """
        raise NotImplementedError

    @abstractmethod
    async def parse(
        self,
        text: str,
        configuration: NLPConfiguration
    ) -> NLPDocument:
        """
        Parse text into a normalized NLP document.
        """
        raise NotImplementedError