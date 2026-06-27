from pathlib import Path
import xml.etree.ElementTree as ET

from app.modules.ingestion.parsers.base_parser import (
    BaseParser
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument
)


class XmlParser(
    BaseParser
):

    @property
    def parser_code(
        self
    ) -> str:

        return "XML"

    @property
    def supported_extensions(
        self
    ) -> set[str]:

        return {
            ".xml"
        }

    @property
    def supported_mime_types(
        self
    ) -> set[str]:

        return {
            "application/xml",
            "text/xml"
        }

    async def parse(
        self,
        file_path: Path,
        configuration: dict | None = None
    ) -> ParsedDocument:

        tree = ET.parse(
            file_path
        )

        root = tree.getroot()

        extracted_text = []

        for element in root.iter():

            if element.text:

                text = element.text.strip()

                if text:

                    extracted_text.append(
                        text
                    )

        text_content = "\n".join(
            extracted_text
        )

        return ParsedDocument(

            file_name=file_path.name,

            file_extension=file_path.suffix.lower(),

            mime_type="application/xml",

            parser_code=self.parser_code,

            title=root.tag,

            language=None,

            page_count=None,

            character_count=len(
                text_content
            ),

            text_content=text_content,

            metadata={

                "root_tag": root.tag,

                "element_count": sum(
                    1
                    for _
                    in
                    root.iter()
                )

            }

        )


xml_parser = XmlParser()