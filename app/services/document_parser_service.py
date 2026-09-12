import os

from app.services.file_parser_service import (
    parse_pdf,
    parse_docx,
    parse_txt,
    parse_csv,
    parse_xlsx,
    parse_pptx,
    parse_image
)


async def parse_document(file_path: str):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":

        return parse_pdf(file_path)

    elif extension == ".docx":

        return parse_docx(file_path)

    elif extension == ".txt":

        return parse_txt(file_path)

    elif extension == ".csv":

        return parse_csv(file_path)

    elif extension == ".xlsx":

        return parse_xlsx(file_path)

    elif extension == ".pptx":

        return parse_pptx(file_path)

    elif extension in [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]:

        return await parse_image(file_path)

    else:

        raise ValueError(
            f"Unsupported document type: {extension}"
        )