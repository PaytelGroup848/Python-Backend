from pathlib import Path

import easyocr

from PIL import Image

from app.modules.ingestion.ocr.base_ocr import (
    BaseOCR
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class EasyOCRProvider(
    BaseOCR
):

    def __init__(
        self
    ):

        self._reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

    @property
    def provider_code(
        self
    ) -> str:

        return "EASY_OCR"

    async def extract_text(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:

        languages = ["en"]

        if configuration:

            languages = configuration.get(
                "languages",
                languages
            )

            if languages != ["en"]:

                self._reader = easyocr.Reader(
                    languages,
                    gpu=False
                )

        image = Image.open(
            file_path
        )

        results = self._reader.readtext(
            image
        )

        extracted_text = []

        confidence_scores = []

        for result in results:

            extracted_text.append(
                result[1]
            )

            confidence_scores.append(
                result[2]
            )

        text_content = "\n".join(
            extracted_text
        )

        average_confidence = None

        if confidence_scores:

            average_confidence = (
                sum(confidence_scores)
                /
                len(confidence_scores)
            )

        return ParsedDocument(

            file_name=file_path.name,

            file_extension=file_path.suffix.lower(),

            mime_type="image",

            parser_code=self.provider_code,

            title=file_path.stem,

            language=",".join(
                languages
            ),

            page_count=None,

            character_count=len(
                text_content
            ),

            text_content=text_content,

            metadata={

                "ocr_provider": self.provider_code,

                "detected_blocks": len(
                    results
                ),

                "average_confidence": average_confidence

            }

        )


easy_ocr = EasyOCRProvider()