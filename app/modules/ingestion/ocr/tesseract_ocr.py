from pathlib import Path

import pytesseract

from PIL import Image

from app.modules.ingestion.ocr.base_ocr import (
    BaseOCR
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class TesseractOCRProvider(
    BaseOCR
):

    @property
    def provider_code(
        self
    ) -> str:

        return "TESSERACT"

    async def extract_text(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:

        image = Image.open(
            file_path
        )

        language = "eng"

        if configuration:

            language = configuration.get(
                "language",
                language
            )

        text_content = pytesseract.image_to_string(

            image,

            lang=language

        )

        return ParsedDocument(

            file_name=file_path.name,

            file_extension=file_path.suffix.lower(),

            mime_type="image",

            parser_code=self.provider_code,

            title=file_path.stem,

            language=language,

            page_count=None,

            character_count=len(
                text_content
            ),

            text_content=text_content,

            metadata={

                "ocr_provider": self.provider_code

            }

        )


tesseract_ocr = (
    TesseractOCRProvider()
)