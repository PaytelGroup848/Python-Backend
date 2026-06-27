from app.modules.ingestion.registry.chunker_registry import (
    chunker_registry
)

from app.modules.ingestion.schemas.document_chunk import (
    DocumentChunk
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class ChunkExecutionService:

    async def execute(
        self,
        parsed_document: ParsedDocument,
        chunker_code: str,
        configuration: dict
    ) -> list[DocumentChunk]:

        chunker = chunker_registry.get_chunker(
            chunker_code
        )

        chunks = await chunker.chunk(
            parsed_document=parsed_document,
            configuration=configuration
        )

        if not isinstance(
            chunks,
            list
        ):
            raise BusinessException(
                "Chunker returned an invalid response."
            )

        for chunk in chunks:

            if not isinstance(
                chunk,
                DocumentChunk
            ):
                raise BusinessException(
                    "Chunker returned an invalid DocumentChunk."
                )

        return chunks


chunk_execution_service = (
    ChunkExecutionService()
)