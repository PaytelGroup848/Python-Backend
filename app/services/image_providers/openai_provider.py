import base64
import logging
import os
from typing import Tuple

import httpx

from app.services.image_providers.base import (
    BaseImageProvider,
    ContentPolicyViolationError,
    ProviderAPIError,
    ProviderTimeoutError,
)

logger = logging.getLogger(__name__)


class OpenAIImageProvider(BaseImageProvider):
    def __init__(self, api_key: str | None = None, timeout_seconds: float = 60.0):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return "dall-e-3"

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Tuple[bytes, str]:
        if not self.api_key:
            raise ProviderAPIError("OPENAI_API_KEY is not configured in backend environment.")

        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    item = data.get("data", [{}])[0]
                    revised_prompt = item.get("revised_prompt") or prompt

                    b64_str = item.get("b64_json")
                    if b64_str:
                        return base64.b64decode(b64_str), revised_prompt

                    img_url = item.get("url")
                    if img_url:
                        dl_res = await client.get(img_url)
                        if dl_res.status_code == 200 and len(dl_res.content) > 1000:
                            return dl_res.content, revised_prompt

                    raise ProviderAPIError("OpenAI returned no usable b64_json or image URL.")
        except httpx.TimeoutException as exc:
            logger.warning(f"OpenAI DALL-E 3 request timed out: {exc}")
            raise ProviderTimeoutError(f"OpenAI DALL-E 3 timed out after {self.timeout_seconds}s") from exc
        except Exception as exc:
            logger.error(f"OpenAI DALL-E 3 connection failure: {exc}")
            raise ProviderAPIError(f"OpenAI connection failure: {exc}") from exc

        if response.status_code != 200:
            err_data = {}
            try:
                err_data = response.json().get("error", {})
            except Exception:
                pass

            err_code = err_data.get("code")
            err_msg = err_data.get("message", response.text)

            # Strict policy: do not retry content policy rejections
            if response.status_code == 400 and (err_code == "content_policy_violation" or "safety" in err_msg.lower() or "policy" in err_msg.lower()):
                logger.warning(f"OpenAI rejected prompt due to content safety policy: {err_msg}")
                raise ContentPolicyViolationError(f"Your prompt was rejected by the content safety system: {err_msg}")

            if response.status_code >= 500 or response.status_code == 429:
                logger.warning(f"OpenAI image generation error ({response.status_code}): {err_msg}")
                raise ProviderAPIError(f"OpenAI service error ({response.status_code}): {err_msg}")

            raise ProviderAPIError(f"OpenAI image request failed ({response.status_code}): {err_msg}")

        raise ProviderAPIError("Failed to extract image from OpenAI response.")
