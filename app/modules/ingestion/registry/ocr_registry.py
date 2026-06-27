from app.modules.ingestion.ocr.base_ocr import (
    BaseOCR
)

from app.shared.exceptions.business_exception import (
    BusinessException
)
from app.modules.ingestion.ocr.paddle_ocr import (
    paddle_ocr
)
from app.modules.ingestion.ocr.tesseract_ocr import (
    tesseract_ocr
)
from app.modules.ingestion.ocr.easy_ocr import (
    easy_ocr
)
class OCRRegistry:

    def __init__(self):

        self._providers: dict[str, BaseOCR] = {}

        self.register(
            paddle_ocr
        )

        self.register(
            tesseract_ocr
        )

        self.register(
            easy_ocr
        )

    def register(
        self,
        provider: BaseOCR
    ) -> None:

        provider_code = provider.provider_code.upper()

        if provider_code in self._providers:

            raise BusinessException(
                f"OCR provider '{provider_code}' is already registered."
            )

        self._providers[
            provider_code
        ] = provider

    def get_provider(
        self,
        provider_code: str
    ) -> BaseOCR:

        provider = self._providers.get(
            provider_code.upper()
        )

        if provider is None:

            raise BusinessException(
                f"OCR provider '{provider_code}' is not registered."
            )

        return provider

    @property
    def providers(
        self
    ) -> dict[str, BaseOCR]:

        return self._providers.copy()


ocr_registry = OCRRegistry()