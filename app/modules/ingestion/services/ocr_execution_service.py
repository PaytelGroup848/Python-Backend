from pathlib import Path

from app.modules.ingestion.registry.ocr_registry import (
    ocr_registry
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class OCRExecutionService:

    async def execute(
        self,
        file_path: Path,
        provider_code: str,
        configuration: dict | None = None
    ) -> ParsedDocument:

        if not file_path.exists():

            raise BusinessException(
                f"File '{file_path}' does not exist."
            )

        provider = ocr_registry.get_provider(
            provider_code
        )

        parsed_document = await provider.extract_text(
            file_path=file_path,
            configuration=configuration
        )

        if not isinstance(
            parsed_document,
            ParsedDocument
        ):

            raise BusinessException(
                "OCR provider returned an invalid ParsedDocument."
            )

        return parsed_document


ocr_execution_service = (
    OCRExecutionService()
)