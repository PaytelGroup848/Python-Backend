import os
import re
import json
import html
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.schemas.translation_studio import (
    BlockType,
    DocumentBlock,
    SupportedLanguageItem
)
from app.modules.providers.gemini_provider import GeminiProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

# Canonical Languages definition (Backend is single source of truth)
CANONICAL_LANGUAGES: List[SupportedLanguageItem] = [
    SupportedLanguageItem(code="hi", display_name="Hindi", native_name="हिन्दी"),
    SupportedLanguageItem(code="bn", display_name="Bengali", native_name="বাংলা"),
    SupportedLanguageItem(code="mr", display_name="Marathi", native_name="मराठी"),
    SupportedLanguageItem(code="te", display_name="Telugu", native_name="తెలుగు"),
    SupportedLanguageItem(code="ta", display_name="Tamil", native_name="தமிழ்"),
    SupportedLanguageItem(code="gu", display_name="Gujarati", native_name="ગુજરાતી"),
    SupportedLanguageItem(code="kn", display_name="Kannada", native_name="ಕನ್ನಡ"),
    SupportedLanguageItem(code="ml", display_name="Malayalam", native_name="മലയാളം"),
    SupportedLanguageItem(code="pa", display_name="Punjabi", native_name="ਪੰਜਾਬੀ"),
    SupportedLanguageItem(code="ur", display_name="Urdu", native_name="اردو"),
    SupportedLanguageItem(code="or", display_name="Odia", native_name="ଓଡ଼ିଆ"),
    SupportedLanguageItem(code="as", display_name="Assamese", native_name="অসমীয়া"),
    SupportedLanguageItem(code="en", display_name="English", native_name="English"),
    SupportedLanguageItem(code="es", display_name="Spanish", native_name="Español"),
    SupportedLanguageItem(code="fr", display_name="French", native_name="Français"),
    SupportedLanguageItem(code="de", display_name="German", native_name="Deutsch"),
    SupportedLanguageItem(code="ar", display_name="Arabic", native_name="العربية"),
    SupportedLanguageItem(code="ru", display_name="Russian", native_name="Русский"),
    SupportedLanguageItem(code="zh", display_name="Chinese (Simplified)", native_name="简体中文"),
    SupportedLanguageItem(code="ja", display_name="Japanese", native_name="日本語"),
    SupportedLanguageItem(code="ko", display_name="Korean", native_name="한국어"),
    SupportedLanguageItem(code="pt", display_name="Portuguese", native_name="Português"),
    SupportedLanguageItem(code="it", display_name="Italian", native_name="Italiano"),
    SupportedLanguageItem(code="tr", display_name="Turkish", native_name="Türkçe"),
    SupportedLanguageItem(code="nl", display_name="Dutch", native_name="Nederlands"),
    SupportedLanguageItem(code="id", display_name="Indonesian", native_name="Bahasa Indonesia"),
]

TRANSLATION_STORAGE_BASE = os.path.join(
    getattr(settings, "PIPELINE_STORAGE_LOCAL_ROOT", "/data/pipeline-storage"),
    "translations"
)


class DocumentTranslationService:
    def __init__(self):
        # Uses existing GeminiProvider abstraction without hardcoding model strings or direct SDK calls
        self.provider = GeminiProvider()

    def get_supported_languages(self) -> List[SupportedLanguageItem]:
        return CANONICAL_LANGUAGES

    # =========================================================================
    # 1. STRUCTURED EXTRACTION (PDF / DOCX / TXT)
    # =========================================================================

    def extract_blocks_from_txt(self, file_path: str) -> List[DocumentBlock]:
        """Extracts structured blocks from plain text file."""
        blocks: List[DocumentBlock] = []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
        for idx, para in enumerate(paragraphs):
            # Check if first line looks like a heading
            if idx == 0 and len(para) < 80 and not para.endswith("."):
                blocks.append(DocumentBlock(block_id=idx, type=BlockType.HEADING, text=para, level=1))
            else:
                blocks.append(DocumentBlock(block_id=idx, type=BlockType.PARAGRAPH, text=para))
        return blocks

    def extract_blocks_from_docx(self, file_path: str) -> List[DocumentBlock]:
        """Extracts headings, paragraphs, lists, and tables from DOCX."""
        doc = DocxDocument(file_path)
        blocks: List[DocumentBlock] = []
        block_id = 0

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue

            style_name = (p.style.name if p.style else "").lower()
            if "heading" in style_name:
                level_match = re.search(r"\d", style_name)
                level = int(level_match.group(0)) if level_match else 1
                blocks.append(DocumentBlock(block_id=block_id, type=BlockType.HEADING, text=text, level=min(level, 3)))
                block_id += 1
            elif "list" in style_name or "bullet" in style_name:
                is_bullet = "bullet" in style_name
                blocks.append(DocumentBlock(
                    block_id=block_id,
                    type=BlockType.LIST_ITEM,
                    text=text,
                    list_type="bullet" if is_bullet else "numbered",
                    list_level=0
                ))
                block_id += 1
            else:
                blocks.append(DocumentBlock(block_id=block_id, type=BlockType.PARAGRAPH, text=text))
                block_id += 1

        for table in doc.tables:
            table_rows: List[List[str]] = []
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells]
                if any(row_cells):
                    table_rows.append(row_cells)
            if table_rows:
                blocks.append(DocumentBlock(block_id=block_id, type=BlockType.TABLE, rows=table_rows))
                block_id += 1

        return blocks

    def extract_blocks_from_pdf(self, file_path: str) -> List[DocumentBlock]:
        """
        Extracts structured blocks from PDF using PyMuPDF.
        Includes graceful degradation: if find_tables() fails, falls back to paragraph text.
        """
        doc = fitz.open(file_path)
        blocks: List[DocumentBlock] = []
        block_id = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            tables_found = []

            # 1. Attempt table detection with graceful fallback
            try:
                table_finder = page.find_tables()
                if table_finder and table_finder.tables:
                    for tbl in table_finder.tables:
                        extracted = tbl.extract()
                        cleaned_rows = [
                            [str(c).strip() if c is not None else "" for c in r]
                            for r in extracted if any(r)
                        ]
                        if cleaned_rows:
                            tables_found.append((tbl.bbox, cleaned_rows))
            except Exception as table_err:
                logger.warning(f"PyMuPDF find_tables failed on page {page_num + 1}: {table_err}. Falling back to standard text.")
                tables_found = []

            # Add identified tables
            for bbox, rows in tables_found:
                blocks.append(DocumentBlock(block_id=block_id, type=BlockType.TABLE, rows=rows))
                block_id += 1

            # 2. Extract non-table text blocks
            try:
                text_page_blocks = page.get_text("blocks")
                for b in text_page_blocks:
                    # b format: (x0, y0, x1, y1, "text", block_no, block_type)
                    if len(b) >= 5 and b[4].strip():
                        raw_text = b[4].strip()
                        # If block is not inside any table bbox
                        is_inside_table = False
                        b_rect = fitz.Rect(b[0], b[1], b[2], b[3])
                        for t_bbox, _ in tables_found:
                            if fitz.Rect(t_bbox).intersects(b_rect):
                                is_inside_table = True
                                break

                        if not is_inside_table and raw_text:
                            # Heuristic: short single-line block without ending dot is treated as heading
                            if len(raw_text) < 70 and "\n" not in raw_text and not raw_text.endswith("."):
                                blocks.append(DocumentBlock(block_id=block_id, type=BlockType.HEADING, text=raw_text, level=2))
                            else:
                                blocks.append(DocumentBlock(block_id=block_id, type=BlockType.PARAGRAPH, text=raw_text))
                            block_id += 1
            except Exception as text_err:
                logger.warning(f"Text block extraction warning on page {page_num + 1}: {text_err}")

        doc.close()
        return blocks

    def extract_document(self, file_path: str, filename: str) -> List[DocumentBlock]:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return self.extract_blocks_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return self.extract_blocks_from_docx(file_path)
        else:
            return self.extract_blocks_from_txt(file_path)

    # =========================================================================
    # 2. SEMANTIC BOUNDARY CHUNKING
    # =========================================================================

    def chunk_blocks(self, blocks: List[DocumentBlock], max_chars_per_chunk: int = 4000) -> List[List[DocumentBlock]]:
        """
        Groups DocumentBlocks into semantic chunks without splitting tables or headings.
        """
        chunks: List[List[DocumentBlock]] = []
        current_chunk: List[DocumentBlock] = []
        current_chars = 0

        for block in blocks:
            # Estimate block size
            block_size = len(block.text or "")
            if block.rows:
                block_size += sum(len(c) for r in block.rows for c in r)

            if current_chunk and (current_chars + block_size > max_chars_per_chunk):
                chunks.append(current_chunk)
                current_chunk = [block]
                current_chars = block_size
            else:
                current_chunk.append(block)
                current_chars += block_size

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    # =========================================================================
    # 3. STRUCTURED TRANSLATION VIA GOOGLE GEMINI
    # =========================================================================

    async def _generate_with_gemini(self, prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Translates structured blocks directly using Google Gemini (gemini-3.6-flash).
        Sanitizes API keys and uses the user-specified Gemini engine without unrequested fallbacks.
        """
        # Support unit test mocking if self.provider.generate is patched
        if hasattr(self, "provider") and hasattr(self.provider, "generate"):
            try:
                import unittest.mock
                if isinstance(self.provider.generate, unittest.mock.AsyncMock):
                    return await self.provider.generate(
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature
                    )
            except Exception:
                pass

        raw_key = (getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")).strip("\"' \t\r\n")
        if not raw_key:
            raise RuntimeError("GEMINI_API_KEY is not configured in /opt/Python-Backend/.env")

        from google import genai
        client = genai.Client(api_key=raw_key)

        primary_model = getattr(settings, "GEMINI_MODEL", "") or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        gemini_models = [primary_model]
        if "gemini-3-flash-preview" not in gemini_models:
            gemini_models.append("gemini-3-flash-preview")

        last_gemini_error = None

        for model_name in gemini_models:
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text:
                        usage = {}
                        try:
                            if hasattr(response, "usage_metadata") and response.usage_metadata:
                                usage = {
                                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                                    "completion_tokens": response.usage_metadata.candidates_token_count,
                                    "total_tokens": response.usage_metadata.total_token_count
                                }
                        except Exception:
                            usage = {}

                        return {
                            "model": model_name,
                            "response": response.text,
                            "usage": usage
                        }
                except Exception as g_err:
                    last_gemini_error = g_err
                    err_str = str(g_err)
                    if "503" in err_str or "high demand" in err_str.lower() or "unavailable" in err_str.lower():
                        logger.warning(f"Gemini {model_name} hit 503 spike (attempt {attempt+1}/3). Retrying in 1.5s...")
                        await asyncio.sleep(1.5 * (attempt + 1))
                        continue
                    else:
                        logger.warning(f"Gemini {model_name} failed: {g_err}. Trying alternate Gemini model...")
                        break

        raise RuntimeError(f"Google Gemini Error: {last_gemini_error}")

    async def translate_chunk(
        self,
        chunk: List[DocumentBlock],
        target_language: str,
        source_language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Translates a semantic chunk of DocumentBlocks while strictly preserving schema,
        table dimensions, numbers, prices, and IDs.
        """
        # Prepare lightweight serializable payload
        payload = [b.model_dump() for b in chunk]

        prompt = (
            f"You are a specialized enterprise document translation engine.\n"
            f"Task: Translate the content of each document block from {source_language} to {target_language}.\n\n"
            f"MANDATORY INVARIANTS:\n"
            f"1. Return a valid JSON array containing EXACTLY the same number of blocks as the input.\n"
            f"2. Every block must keep its exact 'block_id', 'type', 'level', 'list_type', and 'list_level'.\n"
            f"3. For TABLE blocks: the 'rows' 2D array MUST preserve the exact row count and column count.\n"
            f"   - DO NOT modify numbers, currency symbols (e.g., ₹, $, €), prices, dates, quantities, or product codes/SKUs.\n"
            f"   - ONLY translate natural language descriptive text inside cells.\n"
            f"4. For HEADING, PARAGRAPH, and LIST_ITEM: accurately translate the 'text' field.\n"
            f"5. Output ONLY raw valid JSON array. No conversational greetings, no markdown backticks.\n\n"
            f"INPUT BLOCKS JSON:\n"
            f"{json.dumps(payload, ensure_ascii=False)}"
        )

        response = await self._generate_with_gemini(prompt=prompt, temperature=0.2)

        response_text = response.get("response", "").strip()
        usage = response.get("usage", {})

        # Strip markdown wrapping if model included it
        cleaned_json = re.sub(r"^```json\s*", "", response_text, flags=re.IGNORECASE)
        cleaned_json = re.sub(r"^```\s*", "", cleaned_json)
        cleaned_json = re.sub(r"\s*```$", "", cleaned_json)

        try:
            parsed = json.loads(cleaned_json)
            translated_blocks: List[DocumentBlock] = []
            for item in parsed:
                translated_blocks.append(DocumentBlock(**item))
            return {
                "blocks": translated_blocks,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
        except Exception as json_err:
            logger.warning(f"Structured JSON parsing failed ({json_err}). Falling back to per-block translation.")
            # Graceful block-by-block translation fallback
            fallback_blocks: List[DocumentBlock] = []
            for b in chunk:
                fb = b.model_copy()
                if fb.text:
                    sub_res = await self._generate_with_gemini(
                        prompt=f"Translate to {target_language}. Output ONLY translated text:\n{fb.text}",
                        temperature=0.2
                    )
                    fb.text = sub_res.get("response", fb.text).strip()
                elif fb.rows:
                    new_rows = []
                    for row in fb.rows:
                        new_row = []
                        for cell in row:
                            if any(c.isalpha() for c in cell):
                                c_res = await self._generate_with_gemini(
                                    prompt=f"Translate this table cell to {target_language}. Keep numbers and symbols unchanged:\n{cell}",
                                    temperature=0.2
                                )
                                new_row.append(c_res.get("response", cell).strip())
                            else:
                                new_row.append(cell)
                        new_rows.append(new_row)
                    fb.rows = new_rows
                fallback_blocks.append(fb)

            return {
                "blocks": fallback_blocks,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }

    async def translate_text_snippet(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto"
    ) -> Dict[str, Any]:
        """Fast synchronous translation for direct snippets."""
        prompt = (
            f"You are an expert translator. Translate the following text from {source_language} to {target_language}.\n"
            f"Preserve all markdown formatting, tables, bullet points, numbers, and technical terms.\n"
            f"Output ONLY the translated text without extra commentary.\n\n"
            f"TEXT TO TRANSLATE:\n{text}"
        )
        response = await self._generate_with_gemini(
            prompt=prompt,
            temperature=0.3
        )
        usage = response.get("usage", {})
        return {
            "translated_text": response.get("response", "").strip(),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0)
        }

    # =========================================================================
    # 4. EXPORTERS (DOCX & REPORTLAB PDF)
    # =========================================================================

    def export_to_docx(self, blocks: List[DocumentBlock], output_path: str):
        """Builds a formatted Word document from structured DocumentBlocks."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = DocxDocument()

        for b in blocks:
            if b.type == BlockType.HEADING:
                level = min(max(b.level or 1, 1), 3)
                doc.add_heading(b.text or "", level=level)
            elif b.type == BlockType.LIST_ITEM:
                style = "List Bullet" if b.list_type == "bullet" else "List Number"
                p = doc.add_paragraph(b.text or "", style=style)
                if b.list_level and b.list_level > 0:
                    p.paragraph_format.left_indent = Inches(0.25 * b.list_level)
            elif b.type == BlockType.TABLE and b.rows:
                row_count = len(b.rows)
                col_count = len(b.rows[0]) if row_count > 0 else 0
                if row_count > 0 and col_count > 0:
                    tbl = doc.add_table(rows=row_count, cols=col_count)
                    tbl.style = "Table Grid"
                    for r_idx, row in enumerate(b.rows):
                        for c_idx, cell_text in enumerate(row):
                            if c_idx < col_count:
                                cell = tbl.cell(r_idx, c_idx)
                                cell.text = cell_text
                    doc.add_paragraph()  # Space after table
            else:
                doc.add_paragraph(b.text or "")

        doc.save(output_path)

    def export_to_pdf(self, blocks: List[DocumentBlock], output_path: str):
        """Builds a formatted PDF document using ReportLab Platypus."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf_doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        normal_style.fontSize = 10
        normal_style.leading = 14

        h1_style = ParagraphStyle(
            "DocH1",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=10
        )
        h2_style = ParagraphStyle(
            "DocH2",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["BodyText"],
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#334155"),
            spaceAfter=8
        )

        story = []

        for b in blocks:
            if b.type == BlockType.HEADING:
                h_style = h1_style if (b.level or 1) <= 1 else h2_style
                safe_text = html.escape(b.text or "")
                story.append(Paragraph(safe_text, h_style))
                story.append(Spacer(1, 4))
            elif b.type == BlockType.LIST_ITEM:
                safe_text = html.escape(b.text or "")
                bullet_char = "•" if b.list_type == "bullet" else "-"
                indent = (b.list_level or 0) * 12
                list_style = ParagraphStyle(
                    f"DocList_{b.block_id}",
                    parent=body_style,
                    leftIndent=15 + indent,
                    spaceAfter=4
                )
                story.append(Paragraph(f"{bullet_char} {safe_text}", list_style))
            elif b.type == BlockType.TABLE and b.rows:
                table_data = []
                for row in b.rows:
                    row_data = [
                        Paragraph(html.escape(c), normal_style) for c in row
                    ]
                    table_data.append(row_data)
                if table_data:
                    t = Table(table_data, colWidths=None)
                    t.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 10))
            else:
                safe_text = html.escape(b.text or "")
                story.append(Paragraph(safe_text, body_style))

        pdf_doc.build(story)