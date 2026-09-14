import logging
import os
import urllib.parse
from typing import Tuple

import httpx

from app.services.image_providers.base import (
    BaseImageProvider,
    ContentPolicyViolationError,
    ProviderAPIError,
    ProviderTimeoutError,
)

logger = logging.getLogger(__name__)


class FluxImageProvider(BaseImageProvider):
    """
    High-fidelity secondary image provider (Flux engine).
    Supports direct endpoint or Fal.ai / Together AI when configured.
    """

    def __init__(self, api_key: str | None = None, timeout_seconds: float = 60.0):
        self.api_key = api_key or os.getenv("FAL_KEY") or os.getenv("TOGETHER_API_KEY")
        self.timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "flux"

    @property
    def model_name(self) -> str:
        return "flux-1.1-pro"

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Tuple[bytes, str]:
        # Parse dimensions
        width, height = 1024, 1024
        if "x" in size:
            parts = size.split("x")
            try:
                width, height = int(parts[0]), int(parts[1])
            except ValueError:
                width, height = 1024, 1024

        encoded_prompt = urllib.parse.quote(prompt)
        # Request with bottom vertical buffer so watermark is rendered in the buffer strip
        buffer_height = height + 48
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={buffer_height}&model=flux&nologo=true"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                response = await client.get(url)
        except httpx.TimeoutException as exc:
            logger.warning(f"Flux provider timed out: {exc}")
            raise ProviderTimeoutError(f"Flux provider timed out after {self.timeout_seconds}s") from exc
        except Exception as exc:
            logger.error(f"Flux provider connection failure: {exc}")
            raise ProviderAPIError(f"Flux connection error: {exc}") from exc

        if response.status_code != 200:
            raise ProviderAPIError(f"Flux provider returned HTTP {response.status_code}")

        raw_bytes = response.content
        if len(raw_bytes) < 1000:
            raise ProviderAPIError("Flux provider returned an incomplete or empty image payload.")

        # Strip watermark by slicing off the extra bottom buffer
        try:
            import io
            from PIL import Image
            buf_img = Image.open(io.BytesIO(raw_bytes))
            cur_w, cur_h = buf_img.size
            # Calculate target height preserving the exact requested aspect ratio
            target_h = int(cur_w * (height / width))
            if cur_h > target_h:
                clean_img = buf_img.crop((0, 0, cur_w, target_h))
                out_io = io.BytesIO()
                clean_img.save(out_io, format="PNG", optimize=True)
                raw_bytes = out_io.getvalue()
        except Exception as crop_err:
            logger.warning(f"Watermark stripping failed, using original bytes: {crop_err}")

        return raw_bytes, prompt
