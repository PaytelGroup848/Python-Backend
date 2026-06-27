from pydantic import (
    BaseModel,
    ConfigDict
)


class ParserConfiguration(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True
    )

    parser_code: str

    extract_metadata: bool

    preserve_formatting: bool

    detect_language: bool