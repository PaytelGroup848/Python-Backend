from pathlib import Path

import csv

from app.modules.ingestion.parsers.base_parser import (
    BaseParser
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class CsvParser(
    BaseParser
):

    @property
    def parser_code(
        self
    ) -> str:

        return "CSV"

    @property
    def supported_extensions(
        self
    ) -> set[str]:

        return {
            ".csv"
        }

    @property
    def supported_mime_types(
        self
    ) -> set[str]:

        return {
            "text/csv"
        }

    async def parse(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:

        encoding = "utf-8"

        delimiter = ","

        if configuration:

            encoding = configuration.get(
                "encoding",
                encoding
            )

            delimiter = configuration.get(
                "delimiter",
                delimiter
            )

        rows = []

        with open(
            file_path,
            mode="r",
            encoding=encoding,
            newline=""
        ) as csv_file:

            reader = csv.reader(
                csv_file,
                delimiter=delimiter
            )

            for row in reader:

                rows.append(
                    " | ".join(row)
                )

        text_content = "\n".join(
            rows
        )

        return ParsedDocument(

            file_name=file_path.name,

            file_extension=file_path.suffix.lower(),

            mime_type="text/csv",

            parser_code=self.parser_code,

            title=file_path.stem,

            language=None,

            page_count=None,

            character_count=len(
                text_content
            ),

            text_content=text_content,

            metadata={

                "encoding": encoding,

                "delimiter": delimiter,

                "row_count": len(rows)

            }

        )


csv_parser = CsvParser()