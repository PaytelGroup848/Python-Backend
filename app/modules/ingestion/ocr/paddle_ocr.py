import mimetypes

from pathlib import Path

from paddleocr import PaddleOCR

from app.modules.ingestion.ocr.base_ocr import (
    BaseOCR
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class PaddleOCRProvider(
    BaseOCR
):

    @property
    def provider_code(
        self
    ) -> str:

        return "PADDLE_OCR"

    async def extract_text(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:

        configuration = configuration or {}

        language = configuration.get(
            "language",
            "en"
        )

        use_angle_cls = configuration.get(
            "use_angle_cls",
            True
        )

        title = configuration.get(
            "title",
            file_path.stem
        )

        ocr = PaddleOCR(

            use_angle_cls=use_angle_cls,

            lang=language

        )

        result = ocr.ocr(
            str(file_path)
        )

        extracted_text: list[str] = []

        for page in result:

            if page is None:

                continue

            for line in page:

                extracted_text.append(
                    line[1][0]
                )

        text_content = "\n".join(
            extracted_text
        )

        mime_type, _ = mimetypes.guess_type(
            str(file_path)
        )

        mime_type = (
            mime_type
            or
            "application/octet-stream"
        )

        return ParsedDocument(

            file_name=file_path.name,

            file_extension=file_path.suffix.lower(),

            mime_type=mime_type,

            parser_code=self.provider_code,

            title=title,

            language=language,

            page_count=None,

            character_count=len(
                text_content
            ),

            text_content=text_content,

            metadata={

                "ocr_provider": self.provider_code,

                "use_angle_cls": use_angle_cls,

                "language": language

            }

        )


paddle_ocr = PaddleOCRProvider()