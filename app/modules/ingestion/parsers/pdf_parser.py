from pathlib import Path

import fitz

from app.modules.ingestion.parsers.base_parser import (
    BaseParser
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class PdfParser(
    BaseParser
):

    @property
    def parser_code(
        self
    ) -> str:

        return "PDF"

    @property
    def supported_extensions(
        self
    ) -> set[str]:

        return {
            ".pdf"
        }

    @property
    def supported_mime_types(
        self
    ) -> set[str]:

        return {
            "application/pdf"
        }

    async def parse(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:

        pdf_document = fitz.open(
            file_path
        )

        try:

            metadata = (
                pdf_document.metadata
                or
                {}
            )

            extracted_text: list[str] = []

            for page in pdf_document:

                page_text = page.get_text(
                    "text"
                )

                if page_text:

                    extracted_text.append(
                        page_text
                    )

            text_content = "\n".join(
                extracted_text
            )

            return ParsedDocument(

                file_name=file_path.name,

                file_extension=file_path.suffix.lower(),

                mime_type="application/pdf",

                parser_code=self.parser_code,

                title=metadata.get(
                    "title"
                ),

                language=metadata.get(
                    "language"
                ),

                page_count=pdf_document.page_count,

                character_count=len(
                    text_content
                ),

                text_content=text_content,

                metadata=metadata

            )

        finally:

            pdf_document.close()


pdf_parser = PdfParser()