import json
from pathlib import Path

from app.modules.ingestion.parsers.base_parser import (
    BaseParser,
)

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument,
)


class JsonParser(BaseParser):

    @property
    def parser_code(self) -> str:
        return "JSON"

    @property
    def supported_extensions(self) -> set[str]:
        return {".json", ".jsonl"}

    @property
    def supported_mime_types(self) -> set[str]:
        return {"application/json", "application/x-jsonlines"}

    async def parse(
        self,
        file_path: Path,
        configuration: dict | None = None,
    ) -> ParsedDocument:
        encoding = "utf-8"
        if configuration:
            encoding = configuration.get("encoding", encoding)

        records = []
        ext = file_path.suffix.lower()

        with open(file_path, mode="r", encoding=encoding) as f:
            if ext == ".jsonl":
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            inp = obj.get("prompt") or obj.get("question") or obj.get("input") or obj.get("text") or str(obj)
                            out = obj.get("response") or obj.get("answer") or obj.get("output") or ""
                            line_str = f"Q: {inp}\nA: {out}" if out else str(inp)
                            records.append(line_str)
                        else:
                            records.append(str(obj))
                    except json.JSONDecodeError:
                        continue
            else:
                data = json.load(f)
                if isinstance(data, list):
                    for obj in data:
                        if isinstance(obj, dict):
                            inp = obj.get("prompt") or obj.get("question") or obj.get("input") or obj.get("text") or str(obj)
                            out = obj.get("response") or obj.get("answer") or obj.get("output") or ""
                            line_str = f"Q: {inp}\nA: {out}" if out else str(inp)
                            records.append(line_str)
                        else:
                            records.append(str(obj))
                elif isinstance(data, dict):
                    records.append(json.dumps(data, indent=2))

        text_content = "\n\n".join(records)

        return ParsedDocument(
            file_name=file_path.name,
            file_extension=file_path.suffix.lower(),
            mime_type="application/json",
            parser_code=self.parser_code,
            title=file_path.stem,
            language=None,
            page_count=None,
            character_count=len(text_content),
            text_content=text_content,
            metadata={
                "encoding": encoding,
                "record_count": len(records),
            },
        )


json_parser = JsonParser()
