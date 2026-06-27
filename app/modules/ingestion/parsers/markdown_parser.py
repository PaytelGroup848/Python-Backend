from pathlib import Path

from app.modules.ingestion.parsers.base_parser import (
    BaseParser
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class MarkdownParser(
    BaseParser
):

    @property
    def parser_code(
        self
    ) -> str:

        return "MARKDOWN"

    @property
    def supported_extensions(
        self
    ) -> set[str]:

        return {
            ".md",
            ".markdown"
        }

    @property
    def supported_mime_types(
        self
    ) -> set[str]:

        return {
            "text/markdown",
            "text/x-markdown"
        }

    async def parse(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:

        encoding = "utf-8"

        if configuration:

            encoding = configuration.get(
                "encoding",
                encoding
            )

        text_content = file_path.read_text(
            encoding=encoding
        )

        return ParsedDocument(

            file_name=file_path.name,

            file_extension=file_path.suffix.lower(),

            mime_type="text/markdown",

            parser_code=self.parser_code,

            title=file_path.stem,

            language=None,

            page_count=None,

            character_count=len(
                text_content
            ),

            text_content=text_content,

            metadata={

                "encoding": encoding

            }

        )


markdown_parser = MarkdownParser()