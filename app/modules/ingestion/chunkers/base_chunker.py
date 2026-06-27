from abc import (
    ABC,
    abstractmethod
)

from app.modules.ingestion.schemas.document_chunk import (
    DocumentChunk
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class BaseChunker(
    ABC
):

    @property
    @abstractmethod
    def chunker_code(
        self
    ) -> str:
        """
        Unique chunker identifier.

        Example:
            SENTENCE
            RECURSIVE
            SEMANTIC
            TOKEN
        """
        raise NotImplementedError

    @abstractmethod
    async def chunk(
        self,
        parsed_document: ParsedDocument,
        configuration: dict
    ) -> list[DocumentChunk]:
        """
        Convert a parsed document into normalized chunks.
        """
        raise NotImplementedError