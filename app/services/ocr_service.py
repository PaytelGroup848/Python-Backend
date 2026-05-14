import fitz
import tempfile

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en"
)


async def extract_text_from_scanned_pdf(
    pdf_path: str
):

    extracted_pages = []

    pdf = fitz.open(pdf_path)

    for page_index in range(len(pdf)):

        page = pdf[page_index]

        pix = page.get_pixmap()

        with tempfile.NamedTemporaryFile(
            suffix=".png"
        ) as temp_img:

            pix.save(temp_img.name)

            result = ocr.ocr(
                temp_img.name
            )

            page_text = []

            if result and result[0]:

                for line in result[0]:

                    text = line[1][0]

                    page_text.append(text)

            extracted_pages.append({
                "page_number": page_index + 1,
                "text": "\n".join(page_text)
            })
##
    return extracted_pages