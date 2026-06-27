from app.modules.ingestion.chunkers.base_chunker import (
    BaseChunker
)

from app.modules.ingestion.schemas.document_chunk import (
    DocumentChunk
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)

from app.modules.ingestion.services.tokenizer_execution_service import (
    tokenizer_execution_service
)

from app.modules.pipeline_runtime.schemas.chunk_configuration import (
    ChunkConfiguration
)


class TokenChunker(
    BaseChunker
):

    @property
    def chunker_code(
        self
    ) -> str:

        return "TOKEN"

    async def chunk(
        self,
        parsed_document: ParsedDocument,
        configuration: ChunkConfiguration
    ) -> list[DocumentChunk]:

        text = parsed_document.text_content

        max_characters = (
            configuration.max_characters
        )

        overlap = (
            configuration.overlap_characters
        )

        chunks: list[
            DocumentChunk
        ] = []

        start = 0

        chunk_index = 0

        while start < len(text):

            end = min(

                start + max_characters,

                len(text)

            )

            content = text[
                start:end
            ]

            token_count = (
                await tokenizer_execution_service.count_tokens(

                    text=content,

                    tokenizer_code=configuration.tokenizer_code,

                    configuration=configuration

                )
            )

            chunks.append(

                DocumentChunk(

                    chunk_index=chunk_index,

                    source_document_id=parsed_document.source_document_id,

                    dataset_id=parsed_document.dataset_id,

                    corpus_source_id=parsed_document.corpus_source_id,

                    page_number=None,

                    start_offset=start,

                    end_offset=end,

                    content=content,

                    character_count=len(
                        content
                    ),

                    token_count=token_count,

                    metadata={

                        "chunker": self.chunker_code

                    }

                )

            )

            chunk_index += 1

            if end >= len(text):

                break

            start = max(

                end - overlap,

                start + 1

            )

        return chunks


token_chunker = (
    TokenChunker()
)