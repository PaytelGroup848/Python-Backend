from pathlib import Path

from ebooklib import epub
from bs4 import BeautifulSoup

from app.modules.ingestion.parsers.base_parser import (
    BaseParser
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class EpubParser(
    BaseParser
):

    @property
    def parser_code(
        self
    ) -> str:

        return "EPUB"

    @property
    def supported_extensions(
        self
    ) -> set[str]:

        return {
            ".epub"
        }

    @property
    def supported_mime_types(
        self
    ) -> set[str]:

        return {
            "application/epub+zip"
        }

    async def parse(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:

        book = epub.read_epub(
            str(file_path)
        )

        extracted_text = []

        document_title = file_path.stem

        metadata = {}

        titles = book.get_metadata(
            "DC",
            "title"
        )

        if titles:

            document_title = titles[0][0]

        authors = book.get_metadata(
            "DC",
            "creator"
        )

        if authors:

            metadata["authors"] = [
                author[0]
                for author in authors
            ]

        language = None

        languages = book.get_metadata(
            "DC",
            "language"
        )

        if languages:

            language = languages[0][0]

        for item in book.get_items():

            if (
                item.get_type()
                ==
                epub.ITEM_DOCUMENT
            ):

                soup = BeautifulSoup(
                    item.get_body_content(),
                    "html.parser"
                )

                text = soup.get_text(
                    separator="\n",
                    strip=True
                )

                if text:

                    extracted_text.append(
                        text
                    )

        text_content = "\n\n".join(
            extracted_text
        )

        metadata["document_count"] = len(
            extracted_text
        )

        return ParsedDocument(

            file_name=file_path.name,

            file_extension=file_path.suffix.lower(),

            mime_type="application/epub+zip",

            parser_code=self.parser_code,

            title=document_title,

            language=language,

            page_count=None,

            character_count=len(
                text_content
            ),

            text_content=text_content,

            metadata=metadata

        )


epub_parser = EpubParser()