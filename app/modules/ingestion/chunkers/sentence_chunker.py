from app.modules.ingestion.schemas.nlp_document import (
    NLPSentence
)

from app.modules.ingestion.services.nlp_execution_service import (
    nlp_execution_service
)

from app.modules.pipeline_runtime.schemas.chunk_configuration import (
    ChunkConfiguration
)

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


class SentenceChunker(
    BaseChunker
):

    @property
    def chunker_code(
        self
    ) -> str:

        return "SENTENCE"

    async def chunk(
        self,
        parsed_document: ParsedDocument,
        configuration: ChunkConfiguration
    ) -> list[DocumentChunk]:

        nlp_document = await nlp_execution_service.parse(
            text=parsed_document.text_content,
            provider_code=configuration.nlp_provider_code,
            configuration=configuration
        )

        max_characters = configuration.max_characters

        chunks: list[DocumentChunk] = []

        current_sentences: list[NLPSentence] = []

        current_length = 0

        chunk_index = 0


        for sentence in nlp_document.sentences:

            sentence_text = sentence.text.strip()

            if not sentence_text:

                continue

            sentence_length = (
                sentence.end_offset
                -
                sentence.start_offset
            )

            if (
                current_sentences
                and
                current_length + sentence_length
                > max_characters
            ):

                start_offset = (
                    current_sentences[0].start_offset
                )

                end_offset = (
                    current_sentences[-1].end_offset
                )

                content = parsed_document.text_content[
                    start_offset:end_offset
                ]

               

                chunks.append(

                    DocumentChunk(

                        chunk_index=chunk_index,

                        source_document_id=parsed_document.source_document_id,

                        dataset_id=parsed_document.dataset_id,

                        corpus_source_id=parsed_document.corpus_source_id,

                        page_number=None,

                        start_offset=start_offset,

                        end_offset=end_offset,

                        content=content,

                        character_count=len(
                            content
                        ),

                        token_count = await tokenizer_execution_service.count_tokens(
                            text=content,
                            tokenizer_code=configuration.tokenizer_code,
                            configuration=configuration
                        ),

                        metadata={}

                    )

                )

                chunk_index += 1

                current_sentences = []

                current_length = 0

            current_sentences.append(
                sentence
            )

            current_length += sentence_length

        if current_sentences:

            start_offset = (
                current_sentences[0].start_offset
            )

            end_offset = (
                current_sentences[-1].end_offset
            )

            content = parsed_document.text_content[
                start_offset:end_offset
            ]

           

            chunks.append(

                DocumentChunk(

                    chunk_index=chunk_index,

                    source_document_id=parsed_document.source_document_id,

                    dataset_id=parsed_document.dataset_id,

                    corpus_source_id=parsed_document.corpus_source_id,

                    page_number=None,

                    start_offset=start_offset,

                    end_offset=end_offset,

                    content=content,

                    character_count=len(
                        content
                    ),

                    token_count = await tokenizer_execution_service.count_tokens(
                        text=content,
                        tokenizer_code=configuration.tokenizer_code,
                        configuration=configuration
                    ),

                    metadata={}

                )

            )

        return chunks


sentence_chunker = (
    SentenceChunker()
)