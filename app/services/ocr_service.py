
import os
import asyncio
import logging
import tempfile

import fitz

from paddleocr import PaddleOCR


logger = logging.getLogger(__name__)


ocr = None


def get_ocr():

    global ocr

    if ocr is None:

        logger.info(
            "Initializing PaddleOCR..."
        )

        ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en"
        )

    return ocr


# -----------------------------
# SCANNED PDF OCR
# -----------------------------

async def extract_text_from_scanned_pdf(
    pdf_path: str
):

    if not os.path.exists(pdf_path):

        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    extracted_pages = []

    try:

        with fitz.open(pdf_path) as pdf:

            MAX_OCR_PAGES = 100

            total_pages = min(
                len(pdf),
                MAX_OCR_PAGES
            )

            for page_index in range(total_pages):

                page = pdf[page_index]

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(1, 1)
                )

                temp_img_path = None

                try:

                    with tempfile.NamedTemporaryFile(
                        suffix=".png",
                        delete=False
                    ) as temp_img:

                        temp_img_path = temp_img.name

                    pix.save(temp_img_path)

                    result = await asyncio.wait_for(

                        asyncio.to_thread(
                            get_ocr().ocr,
                            temp_img_path
                        ),

                        timeout=60,
                    )

                    page_text = []

                    if result and result[0]:

                        for line in result[0]:

                            try:

                                text = line[1][0]

                                if text.strip():

                                    page_text.append(text)

                            except Exception:

                                continue

                    extracted_pages.append({

                        "page_number": (
                            page_index + 1
                        ),

                        "text": "\n".join(
                            page_text
                        )
                    })

                except asyncio.TimeoutError:

                    logger.warning(
                        f"OCR timeout on page "
                        f"{page_index + 1}: "
                        f"{pdf_path}"
                    )

                except Exception:

                    logger.exception(
                        f"PDF OCR failed on page "
                        f"{page_index + 1}: "
                        f"{pdf_path}"
                    )

                finally:

                    if (
                        temp_img_path
                        and
                        os.path.exists(
                            temp_img_path
                        )
                    ):

                        try:

                            os.remove(
                                temp_img_path
                            )

                        except Exception:

                            logger.warning(
                                f"Failed to delete "
                                f"temp file: "
                                f"{temp_img_path}"
                            )

        return extracted_pages

    except Exception:

        logger.exception(
            f"Scanned PDF OCR failed: "
            f"{pdf_path}"
        )

        raise


# -----------------------------
# IMAGE OCR
# -----------------------------

async def extract_text_from_image(
    image_path: str
):

    if not os.path.exists(image_path):

        raise FileNotFoundError(
            f"Image not found: "
            f"{image_path}"
        )

    try:

        result = await asyncio.wait_for(

            asyncio.to_thread(
                get_ocr().ocr,
                image_path
            ),

            timeout=60,
        )

        lines = []

        if result and result[0]:

            for line in result[0]:

                try:

                    text = line[1][0]

                    if text.strip():

                        lines.append(text)

                except Exception:

                    continue

        return "\n".join(lines)

    except asyncio.TimeoutError:

        logger.warning(
            f"Image OCR timeout: "
            f"{image_path}"
        )

        raise

    except Exception:

        logger.exception(
            f"Image OCR failed: "
            f"{image_path}"
        )

        raise
