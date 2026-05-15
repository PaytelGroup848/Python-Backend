import pandas as pd

from docx import Document as DocxDocument

from pptx import Presentation

from pypdf import PdfReader

from app.services.ocr_service import (
    extract_text_from_image
)

# -----------------------------
# PDF
# -----------------------------

def parse_pdf(file_path: str):

    reader = PdfReader(file_path)

    pages = []

    for page_num, page in enumerate(reader.pages):

        text = page.extract_text() or ""

        pages.append({
            "page_number": page_num + 1,
            "text": text
        })

    return pages

# -----------------------------
# DOCX
# -----------------------------

def parse_docx(file_path: str):

    doc = DocxDocument(file_path)

    text = "\n".join([
        p.text
        for p in doc.paragraphs
    ])

    return [{
        "page_number": 1,
        "text": text
    }]

# -----------------------------
# TXT
# -----------------------------

def parse_txt(file_path: str):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        text = f.read()

    return [{
        "page_number": 1,
        "text": text
    }]

# -----------------------------
# CSV
# -----------------------------

def parse_csv(file_path: str):

    df = pd.read_csv(file_path)

    text = df.to_string()

    return [{
        "page_number": 1,
        "text": text
    }]

# -----------------------------
# XLSX
# -----------------------------

def parse_xlsx(file_path: str):

    excel = pd.ExcelFile(file_path)

    all_text = []

    for sheet in excel.sheet_names:

        df = pd.read_excel(
            file_path,
            sheet_name=sheet
        )

        all_text.append(df.to_string())

    return [{
        "page_number": 1,
        "text": "\n\n".join(all_text)
    }]

# -----------------------------
# PPTX
# -----------------------------

def parse_pptx(file_path: str):

    prs = Presentation(file_path)

    slides = []

    for idx, slide in enumerate(prs.slides):

        slide_text = []

        for shape in slide.shapes:

            if hasattr(shape, "text"):

                slide_text.append(shape.text)

        slides.append({
            "page_number": idx + 1,
            "text": "\n".join(slide_text)
        })

    return slides

# -----------------------------
# IMAGE OCR
# -----------------------------

async def parse_image(file_path: str):

    text = await extract_text_from_image(
        file_path
    )

    return [{
        "page_number": 1,
        "text": text
    }]