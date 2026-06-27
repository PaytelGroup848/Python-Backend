from pathlib import Path

from bs4 import BeautifulSoup

from app.modules.ingestion.parsers.base_parser import (
    BaseParser
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class HtmlParser(
    BaseParser
):

    @property
    def parser_code(
        self
    ) -> str:

        return "HTML"

    @property
    def supported_extensions(
        self
    ) -> set[str]:

        return {
            ".html",
            ".htm"
        }

    @property
    def supported_mime_types(
        self
    ) -> set[str]:

        return {
            "text/html"
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

        html = file_path.read_text(
            encoding=encoding
        )

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        title = None

        if soup.title:

            title = soup.title.get_text(
                strip=True
            )

        text_content = soup.get_text(
            separator="\n",
            strip=True
        )

        return ParsedDocument(

            file_name=file_path.name,

            file_extension=file_path.suffix.lower(),

            mime_type="text/html",

            parser_code=self.parser_code,

            title=title,

            language=soup.html.get("lang")
            if soup.html
            else None,

            page_count=None,

            character_count=len(
                text_content
            ),

            text_content=text_content,

            metadata={

                "encoding": encoding

            }

        )


html_parser = HtmlParser()