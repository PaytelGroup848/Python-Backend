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


class RecursiveChunker(
    BaseChunker
):

    @property
    def chunker_code(
        self
    ) -> str:

        return "RECURSIVE"

    async def chunk(
        self,
        parsed_document: ParsedDocument,
        configuration: ChunkConfiguration
    ) -> list[
        DocumentChunk
    ]:

        max_characters = (
            configuration.max_characters
        )

        overlap = (
            configuration.overlap_characters
        )

        text = (
            parsed_document.text_content
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

            if end < len(text):

                separator_position = max(

                    text.rfind(
                        "\n\n",
                        start,
                        end
                    ),

                    text.rfind(
                        "\n",
                        start,
                        end
                    ),

                    text.rfind(
                        ". ",
                        start,
                        end
                    ),

                    text.rfind(
                        " ",
                        start,
                        end
                    )

                )

                if separator_position > start:

                    end = separator_position

            content = text[
                start:end
            ].strip()

            if content:

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


recursive_chunker = (
    RecursiveChunker()
)