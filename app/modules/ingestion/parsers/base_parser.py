from abc import (
    ABC,
    abstractmethod
)

from pathlib import Path


class BaseParser(
    ABC
):

    @property
    @abstractmethod
    def parser_code(
        self
    ) -> str:
        """
        Unique parser identifier.

        Examples:
            PDF
            DOCX
            TXT
            CSV
            XLSX
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def supported_extensions(
        self
    ) -> set[str]:
        """
        File extensions supported by this parser.

        Example:
            {".pdf"}
        """
        raise NotImplementedError

    @abstractmethod
    async def parse(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> dict:
        """
        Parse a document.

        Returns a standardized parsing result.
        """
        raise NotImplementedError

    def supports(
        self,
        extension: str
    ) -> bool:

        return (
            extension.lower()
            in
            self.supported_extensions
        )