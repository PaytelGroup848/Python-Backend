from pathlib import Path

from app.modules.ingestion.registry.parser_registry import (
    parser_registry
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument,
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class ParserExecutionService:

    async def execute(
        self,
        file_path: Path,
        mime_type: str | None = None,
        configuration: dict | None = None,
    ) -> ParsedDocument:

        if not file_path.exists():

            raise BusinessException(
                f"File '{file_path}' does not exist."
            )

        parser = parser_registry.resolve(
            file_path=file_path,
            mime_type=mime_type,
        )

        result = await parser.parse(
            file_path=file_path,
            configuration=configuration,
        )

        if not isinstance(
            result,
            ParsedDocument,
        ):

            raise BusinessException(
                "Parser returned an invalid parsed document."
            )

        return result


parser_execution_service = (
    ParserExecutionService()
)