from app.modules.ingestion.chunkers.base_chunker import (
    BaseChunker
)

from app.shared.exceptions.business_exception import (
    BusinessException
)

from app.modules.ingestion.chunkers.sentence_chunker import (
    sentence_chunker
)

from app.modules.ingestion.chunkers.recursive_chunker import (
    recursive_chunker
)

from app.modules.ingestion.chunkers.token_chunker import (
    token_chunker
)

class ChunkerRegistry:

    def __init__(
        self
    ):

        self._chunkers: dict[
            str,
            BaseChunker
        ] = {}

        self.register(
            sentence_chunker
        )

        self.register(
            recursive_chunker
        )

        self.register(
            token_chunker
        )

    def register(
        self,
        chunker: BaseChunker
    ) -> None:

        chunker_code = (
            chunker.chunker_code.upper()
        )

        if chunker_code in self._chunkers:

            raise BusinessException(

                f"Chunker '{chunker_code}' is already registered."

            )

        self._chunkers[
            chunker_code
        ] = chunker

    def get_chunker(
        self,
        chunker_code: str
    ) -> BaseChunker:

        chunker = self._chunkers.get(

            chunker_code.upper()

        )

        if chunker is None:

            raise BusinessException(

                f"Chunker '{chunker_code}' is not registered."

            )

        return chunker

    @property
    def chunkers(
        self
    ) -> dict[
        str,
        BaseChunker
    ]:

        return self._chunkers.copy()


chunker_registry = (
    ChunkerRegistry()
)