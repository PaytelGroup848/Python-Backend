from pathlib import Path

from app.modules.ingestion.parsers.base_parser import (
    BaseParser
)

from app.shared.exceptions.business_exception import (
    BusinessException
)

from app.modules.ingestion.parsers.pdf_parser import (
    pdf_parser
)

from app.modules.ingestion.parsers.docx_parser import (
    docx_parser
)
from app.modules.ingestion.parsers.txt_parser import (
    txt_parser
)
from app.modules.ingestion.parsers.csv_parser import (
    csv_parser
)
from app.modules.ingestion.parsers.xlsx_parser import (
    xlsx_parser
)
from app.modules.ingestion.parsers.markdown_parser import (
    markdown_parser
)
from app.modules.ingestion.parsers.html_parser import (
    html_parser
)
from app.modules.ingestion.parsers.xml_parser import (
    xml_parser
)
from app.modules.ingestion.parsers.epub_parser import (
    epub_parser
)

class ParserRegistry:

    def __init__(self):

        self._parsers: dict[str, BaseParser] = {}

        self.register(
            pdf_parser
        )

        self.register(
            docx_parser
        )

        self.register(
            txt_parser
        )
        self.register(
            csv_parser
        )
        self.register(
            xlsx_parser
        )
        self.register(
            markdown_parser
        )

        self.register(
            html_parser
        )
        self.register(
            xml_parser
        )
        self.register(
            epub_parser
        )

    def register(
        self,
        parser: BaseParser
    ) -> None:

        parser_code = parser.parser_code.upper()

        if parser_code in self._parsers:

            raise BusinessException(
                f"Parser '{parser_code}' is already registered."
            )

        self._parsers[parser_code] = parser

    def get_by_code(
        self,
        parser_code: str
    ) -> BaseParser:

        parser = self._parsers.get(
            parser_code.upper()
        )

        if parser is None:

            raise BusinessException(
                f"Parser '{parser_code}' is not registered."
            )

        return parser

    def get_by_extension(
        self,
        extension: str
    ) -> BaseParser:

        extension = extension.lower()

        for parser in self._parsers.values():

            if extension in parser.supported_extensions:

                return parser

        raise BusinessException(
            f"No parser registered for extension '{extension}'."
        )

    def get_by_mime_type(
        self,
        mime_type: str
    ) -> BaseParser:

        mime_type = mime_type.lower()

        for parser in self._parsers.values():

            if mime_type in parser.supported_mime_types:

                return parser

        raise BusinessException(
            f"No parser registered for MIME type '{mime_type}'."
        )

    def resolve(
        self,
        file_path: Path,
        mime_type: str | None = None
    ) -> BaseParser:

        if mime_type:

            try:

                return self.get_by_mime_type(
                    mime_type
                )

            except BusinessException:

                pass

        return self.get_by_extension(
            file_path.suffix
        )

    @property
    def parsers(
        self
    ) -> dict[str, BaseParser]:

        return self._parsers.copy()


parser_registry = ParserRegistry()