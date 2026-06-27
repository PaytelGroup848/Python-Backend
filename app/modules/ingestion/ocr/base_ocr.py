from abc import (
    ABC,
    abstractmethod
)

from pathlib import Path

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class BaseOCR(
    ABC
):

    @property
    @abstractmethod
    def provider_code(
        self
    ) -> str:
        """
        OCR provider identifier.

        Examples:
            PADDLE_OCR
            TESSERACT
            EASY_OCR
        """
        raise NotImplementedError

    @abstractmethod
    async def extract_text(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:
        """
        Extract text from an image or scanned document.
        """
        raise NotImplementedError