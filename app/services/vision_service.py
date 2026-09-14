import base64
import logging
import os
import requests
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("vision_service")


class VisionService:
    @staticmethod
    async def analyze_image(file_path: str, prompt: Optional[str] = None) -> str:
        """
        Multimodal Vision analysis using Pixtral / Mistral Vision.
        Accepts image file path and optional prompt/question.
        Returns detailed visual description, code, or answers.
        """
        full_path = file_path
        if not os.path.isabs(full_path):
            full_path = os.path.join(os.getcwd(), file_path)

        if not os.path.exists(full_path):
            # Try uploads/ directory
            candidate = os.path.join(os.getcwd(), "uploads", os.path.basename(file_path))
            if os.path.exists(candidate):
                full_path = candidate

        if not os.path.exists(full_path):
            logger.warning(f"Vision image not found at: {file_path}")
            return ""

        try:
            with open(full_path, "rb") as f:
                image_bytes = f.read()

            b64_data = base64.b64encode(image_bytes).decode("utf-8")
            ext = os.path.splitext(full_path)[1].lower().lstrip(".")
            mime = "image/png" if ext == "png" else ("image/webp" if ext == "webp" else "image/jpeg")

            effective_prompt = prompt or (
                "Provide a detailed analysis of this image. Describe all subjects, text, objects, colors, layout, and any relevant details."
            )

            headers = {
                "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "pixtral-12b-2409",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": effective_prompt},
                            {"type": "image_url", "image_url": f"data:{mime};base64,{b64_data}"}
                        ]
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.2,
            }

            # Asynchronously call Mistral vision API
            import asyncio
            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=45
                )
            )

            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content.strip()
            else:
                logger.warning(f"Pixtral vision API returned {resp.status_code}: {resp.text}")

        except Exception as exc:
            logger.error(f"Multimodal vision analysis error: {exc}")

        # Fallback to OCR text extraction
        try:
            from app.services.file_parser_service import extract_text_from_image
            ocr_text = await extract_text_from_image(full_path)
            if ocr_text and ocr_text.strip():
                return f"OCR Text extracted from image:\n{ocr_text.strip()}"
        except Exception:
            pass

        return ""


vision_service = VisionService()
