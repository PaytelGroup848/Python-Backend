import io
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from PIL import Image

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.generated_image import GeneratedImage
from app.models.conversation_session import ConversationSession
from app.models.user import User
from app.modules.usage.services.usage_limit_service import usage_limit_service
from app.shared.redis.client import redis_client
from app.services.image_providers import (
    BaseImageProvider,
    OpenAIImageProvider,
    FluxImageProvider,
    ContentPolicyViolationError,
    ProviderTimeoutError,
    ProviderAPIError,
)

logger = logging.getLogger("image_generation_service")

# Cost in token equivalents for an image generation
IMAGE_TOKEN_COST = 1000


class ImageGenerationService:
    def __init__(self):
        self.primary_provider: BaseImageProvider = OpenAIImageProvider()
        self.fallback_provider: BaseImageProvider = FluxImageProvider()

    async def reserve_credits(self, user_id: int, tokens: int = IMAGE_TOKEN_COST) -> str:
        """
        Phase 1: Reserves credits before calling image generation provider.
        Returns a unique reservation_id.
        """
        reservation_id = str(uuid.uuid4())
        reservation_key = f"image_reservation:{reservation_id}"

        # Verify user has remaining quota/tokens
        async with AsyncSessionLocal() as db:
            allowed = await usage_limit_service.check_usage_limit(db, user_id=user_id)
            if not allowed:
                raise ValueError("Monthly quota or token limit exceeded. Please upgrade your plan.")

        # Store reservation state in Redis with 120s TTL
        payload = {
            "reservation_id": reservation_id,
            "user_id": user_id,
            "tokens": tokens,
            "status": "RESERVED",
            "created_at": datetime.utcnow().isoformat(),
        }
        await redis_client.set(reservation_key, json.dumps(payload), ex=120)
        logger.info(f"Reserved {tokens} tokens for user={user_id} reservation_id={reservation_id}")
        return reservation_id

    async def commit_credits(self, reservation_id: str, user_id: int, tokens: int = IMAGE_TOKEN_COST) -> None:
        """
        Phase 2 (Success): Commits the reserved credits to the user's permanent usage ledger.
        """
        reservation_key = f"image_reservation:{reservation_id}"
        await usage_limit_service.track_usage(user_id, tokens)
        await redis_client.delete(reservation_key)
        logger.info(f"Committed {tokens} tokens for user={user_id} reservation_id={reservation_id}")

    async def rollback_credits(self, reservation_id: str, reason: str = "") -> None:
        """
        Phase 2 (Failure): Releases the reserved credits with no penalty to the user.
        """
        reservation_key = f"image_reservation:{reservation_id}"
        await redis_client.delete(reservation_key)
        logger.warning(f"Rolled back credit reservation {reservation_id}. Reason: {reason}")

    def enhance_prompt(self, user_prompt: str) -> str:
        """
        Expands basic user prompt into visually rich photographic details.
        """
        cleaned = user_prompt.strip()
        # If prompt is already very descriptive (> 20 words), keep it as is
        if len(cleaned.split()) > 20:
            return cleaned

        # Photographic enhancement suffix
        enhancements = "cinematic lighting, ultra-detailed, photorealistic, 8k resolution, crisp focus, masterpiece"
        return f"{cleaned}, {enhancements}"

    def normalize_to_png(self, raw_bytes: bytes) -> bytes:
        """
        Validates image header, decodes via Pillow, and normalizes into optimized PNG bytes.
        """
        try:
            with Image.open(io.BytesIO(raw_bytes)) as img:
                # Convert palette or grayscale images with transparency to RGBA, or RGB
                if img.mode in ("P", "LA"):
                    img = img.convert("RGBA")
                elif img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")

                output = io.BytesIO()
                img.save(output, format="PNG", optimize=True)
                return output.getvalue()
        except Exception as exc:
            logger.error(f"Image normalization failed: {exc}")
            raise ValueError(f"Downloaded payload is not a valid decodable image: {exc}") from exc

    async def generate_and_persist(
        self,
        user_id: int,
        conversation_id: Optional[int],
        prompt: str,
        message_id: Optional[int] = None,
        aspect_ratio: str = "1024x1024",
        parent_image_id: Optional[int] = None,
        edit_type: str = "generation",
    ) -> Dict[str, Any]:
        """
        Executes the full resilient SaaS pipeline:
        1. Reserve credits
        2. Enhance prompt
        3. Call provider with selective fallback
        4. Normalize to PNG
        5. Atomic file write
        6. DB insert
        7. Commit credits
        """
        reservation_id = await self.reserve_credits(user_id=user_id)
        enhanced_prompt = self.enhance_prompt(prompt)

        raw_bytes: bytes | None = None
        used_provider = self.primary_provider.provider_name
        used_model = self.primary_provider.model_name
        revised_prompt = enhanced_prompt

        try:
            # Try Primary Provider (OpenAI DALL-E 3)
            try:
                logger.info(f"Attempting image generation with primary provider: {self.primary_provider.provider_name}")
                raw_bytes, revised = await self.primary_provider.generate(
                    prompt=enhanced_prompt,
                    size=aspect_ratio,
                )
                revised_prompt = revised or enhanced_prompt
            except ContentPolicyViolationError:
                # Content policy violations MUST NOT fallback to another provider
                raise
            except (ProviderTimeoutError, ProviderAPIError, Exception) as primary_err:
                logger.warning(
                    f"Primary provider ({self.primary_provider.provider_name}) failed: {primary_err}. "
                    f"Executing selective fallback to {self.fallback_provider.provider_name}."
                )
                used_provider = self.fallback_provider.provider_name
                used_model = self.fallback_provider.model_name
                raw_bytes, revised = await self.fallback_provider.generate(
                    prompt=enhanced_prompt,
                    size=aspect_ratio,
                )
                revised_prompt = revised or enhanced_prompt

            if not raw_bytes:
                raise ValueError("No image bytes returned by providers.")

            # Step 4: Normalize to verified PNG
            png_bytes = self.normalize_to_png(raw_bytes)

            # Step 5: Atomic filesystem persistence
            now = datetime.utcnow()
            year_str = now.strftime("%Y")
            month_str = now.strftime("%m")
            image_uuid = str(uuid.uuid4())

            base_dir = os.path.join(os.getcwd(), "media", "generated", "images", year_str, month_str)
            os.makedirs(base_dir, exist_ok=True)

            temp_file_path = os.path.join(base_dir, f"{image_uuid}.tmp")
            final_file_path = os.path.join(base_dir, f"{image_uuid}.png")
            relative_file_path = f"media/generated/images/{year_str}/{month_str}/{image_uuid}.png"
            file_url = f"/media/generated/images/{year_str}/{month_str}/{image_uuid}.png"

            # Write temporary file
            with open(temp_file_path, "wb") as f:
                f.write(png_bytes)

            # Atomic rename
            os.replace(temp_file_path, final_file_path)

            # Step 6: PostgreSQL DB Transaction
            try:
                async with AsyncSessionLocal() as db:
                    valid_conv_id = None
                    if conversation_id:
                        conv_check = await db.execute(
                            select(ConversationSession.id).filter(ConversationSession.id == conversation_id)
                        )
                        if conv_check.scalar_one_or_none() is not None:
                            valid_conv_id = conversation_id

                    valid_user_id = user_id
                    user_check = await db.execute(
                        select(User.id).filter(User.id == user_id)
                    )
                    if user_check.scalar_one_or_none() is None:
                        first_user = await db.execute(select(User.id).limit(1))
                        valid_user_id = first_user.scalar_one_or_none() or 1

                    db_row = GeneratedImage(
                        user_id=valid_user_id,
                        conversation_id=valid_conv_id,
                        message_id=message_id,
                        parent_image_id=parent_image_id,
                        edit_type=edit_type,
                        provider=used_provider,
                        model_name=used_model,
                        original_prompt=prompt,
                        enhanced_prompt=revised_prompt,
                        file_path=relative_file_path,
                        file_url=file_url,
                        mime_type="image/png",
                        aspect_ratio=aspect_ratio,
                        status="completed",
                    )
                    db.add(db_row)
                    await db.commit()
            except Exception as db_err:
                logger.error(f"Database insert failed for image asset {image_uuid}: {db_err}")
                if os.path.exists(final_file_path):
                    try:
                        os.remove(final_file_path)
                    except OSError:
                        pass
                raise db_err

            # Step 7: Commit credits on complete success
            await self.commit_credits(reservation_id=reservation_id, user_id=user_id)

            return {
                "file_url": file_url,
                "provider": used_provider,
                "model_name": used_model,
                "original_prompt": prompt,
                "enhanced_prompt": revised_prompt,
                "aspect_ratio": aspect_ratio,
            }

        except ContentPolicyViolationError as cpv:
            await self.rollback_credits(reservation_id=reservation_id, reason="Content policy violation")
            raise cpv
        except Exception as exc:
            await self.rollback_credits(reservation_id=reservation_id, reason=str(exc))
            raise exc

    async def remove_background(
        self,
        user_id: int,
        image_id: Optional[int] = None,
        file_url: Optional[str] = None,
        raw_image_bytes: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Removes background and creates transparent PNG asset using RemBG.
        """
        try:
            import rembg  # type: ignore[import-not-found, import-untyped]
        except ImportError:
            raise RuntimeError(
                "The 'rembg' package is required for background removal. Please ensure it is installed."
            )
        parent_img_record = None
        source_bytes = raw_image_bytes

        if not source_bytes:
            async with AsyncSessionLocal() as db:
                if image_id:
                    res = await db.execute(select(GeneratedImage).filter(GeneratedImage.id == image_id))
                    parent_img_record = res.scalar_one_or_none()
                elif file_url:
                    clean_url = file_url.split("?")[0]
                    if clean_url.startswith("http://") or clean_url.startswith("https://"):
                        from urllib.parse import urlparse
                        clean_url = urlparse(clean_url).path
                    res = await db.execute(
                        select(GeneratedImage).filter(
                            (GeneratedImage.file_url == clean_url) |
                            (GeneratedImage.file_path == clean_url.lstrip("/"))
                        ).order_by(GeneratedImage.id.desc()).limit(1)
                    )
                    parent_img_record = res.scalar_one_or_none()

            if parent_img_record:
                full_path = os.path.join(os.getcwd(), parent_img_record.file_path)
                if not os.path.exists(full_path):
                    full_path = os.path.join(os.getcwd(), "media", *parent_img_record.file_path.split("media/")[-1].split("/"))
                if os.path.exists(full_path):
                    with open(full_path, "rb") as f:
                        source_bytes = f.read()

        if not source_bytes and file_url:
            clean_rel = file_url.split("?")[0]
            if clean_rel.startswith("http://") or clean_rel.startswith("https://"):
                from urllib.parse import urlparse
                clean_rel = urlparse(clean_rel).path
            clean_rel = clean_rel.lstrip("/")
            candidate = os.path.join(os.getcwd(), clean_rel)
            if not os.path.exists(candidate) and "media" in clean_rel:
                candidate = os.path.join(os.getcwd(), "media", *clean_rel.split("media/")[-1].split("/"))
            if os.path.exists(candidate):
                with open(candidate, "rb") as f:
                    source_bytes = f.read()

        if not source_bytes:
            raise ValueError("Source image could not be located on disk or provided bytes are empty.")

        # Run RemBG using cached u2net session
        if not hasattr(self, "_rembg_session") or self._rembg_session is None:
            self._rembg_session = rembg.new_session("u2net")
        output_bytes = rembg.remove(source_bytes, session=self._rembg_session)

        # Save transparent PNG
        now = datetime.utcnow()
        year_str = now.strftime("%Y")
        month_str = now.strftime("%m")
        image_uuid = str(uuid.uuid4())

        base_dir = os.path.join(os.getcwd(), "media", "generated", "images", year_str, month_str)
        os.makedirs(base_dir, exist_ok=True)
        final_file_path = os.path.join(base_dir, f"{image_uuid}_nobg.png")
        relative_file_path = f"media/generated/images/{year_str}/{month_str}/{image_uuid}_nobg.png"
        new_file_url = f"/media/generated/images/{year_str}/{month_str}/{image_uuid}_nobg.png"

        with open(final_file_path, "wb") as f:
            f.write(output_bytes)

        # Insert record into database
        new_id = None
        async with AsyncSessionLocal() as db:
            parent_id = parent_img_record.id if parent_img_record else image_id
            orig_prompt = parent_img_record.original_prompt if parent_img_record else "Transparent Cutout"
            new_record = GeneratedImage(
                user_id=user_id,
                conversation_id=parent_img_record.conversation_id if parent_img_record else None,
                parent_image_id=parent_id,
                edit_type="remove_bg",
                provider="rembg",
                model_name="u2net",
                original_prompt=f"Transparent PNG: {orig_prompt}",
                enhanced_prompt=f"Background removed via RemBG: {orig_prompt}",
                file_path=relative_file_path,
                file_url=new_file_url,
                mime_type="image/png",
                aspect_ratio=parent_img_record.aspect_ratio if parent_img_record else "original",
                status="completed"
            )
            db.add(new_record)
            await db.commit()
            new_id = new_record.id

        return {
            "id": new_id,
            "file_url": new_file_url,
            "parent_image_id": parent_id,
            "edit_type": "remove_bg",
            "status": "completed",
        }

    async def upscale_image(
        self,
        user_id: int,
        image_id: Optional[int] = None,
        file_url: Optional[str] = None,
        raw_image_bytes: Optional[bytes] = None,
        scale: int = 4,
    ) -> Dict[str, Any]:
        """
        Upscales image by 4x using high-fidelity Lanczos resampling and unsharp masking.
        """
        from PIL import ImageFilter
        parent_img_record = None
        source_bytes = raw_image_bytes

        if not source_bytes:
            async with AsyncSessionLocal() as db:
                if image_id:
                    res = await db.execute(select(GeneratedImage).filter(GeneratedImage.id == image_id))
                    parent_img_record = res.scalar_one_or_none()
                elif file_url:
                    clean_url = file_url.split("?")[0]
                    if clean_url.startswith("http://") or clean_url.startswith("https://"):
                        from urllib.parse import urlparse
                        clean_url = urlparse(clean_url).path
                    res = await db.execute(
                        select(GeneratedImage).filter(
                            (GeneratedImage.file_url == clean_url) |
                            (GeneratedImage.file_path == clean_url.lstrip("/"))
                        ).order_by(GeneratedImage.id.desc()).limit(1)
                    )
                    parent_img_record = res.scalar_one_or_none()

            if parent_img_record:
                full_path = os.path.join(os.getcwd(), parent_img_record.file_path)
                if not os.path.exists(full_path):
                    full_path = os.path.join(os.getcwd(), "media", *parent_img_record.file_path.split("media/")[-1].split("/"))
                if os.path.exists(full_path):
                    with open(full_path, "rb") as f:
                        source_bytes = f.read()

        if not source_bytes and file_url:
            clean_rel = file_url.split("?")[0]
            if clean_rel.startswith("http://") or clean_rel.startswith("https://"):
                from urllib.parse import urlparse
                clean_rel = urlparse(clean_rel).path
            clean_rel = clean_rel.lstrip("/")
            candidate = os.path.join(os.getcwd(), clean_rel)
            if not os.path.exists(candidate) and "media" in clean_rel:
                candidate = os.path.join(os.getcwd(), "media", *clean_rel.split("media/")[-1].split("/"))
            if os.path.exists(candidate):
                with open(candidate, "rb") as f:
                    source_bytes = f.read()

        if not source_bytes:
            raise ValueError("Source image could not be located on disk or provided bytes are empty.")

        with Image.open(io.BytesIO(source_bytes)) as img:
            new_w = img.width * scale
            new_h = img.height * scale
            upscaled = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
            sharpened = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=130, threshold=2))

            output_io = io.BytesIO()
            sharpened.save(output_io, format="PNG", optimize=True)
            output_bytes = output_io.getvalue()

        now = datetime.utcnow()
        year_str = now.strftime("%Y")
        month_str = now.strftime("%m")
        image_uuid = str(uuid.uuid4())

        base_dir = os.path.join(os.getcwd(), "media", "generated", "images", year_str, month_str)
        os.makedirs(base_dir, exist_ok=True)
        final_file_path = os.path.join(base_dir, f"{image_uuid}_4k.png")
        relative_file_path = f"media/generated/images/{year_str}/{month_str}/{image_uuid}_4k.png"
        new_file_url = f"/media/generated/images/{year_str}/{month_str}/{image_uuid}_4k.png"

        with open(final_file_path, "wb") as f:
            f.write(output_bytes)

        new_id = None
        async with AsyncSessionLocal() as db:
            parent_id = parent_img_record.id if parent_img_record else image_id
            orig_prompt = parent_img_record.original_prompt if parent_img_record else "4K Super-Resolution"
            new_record = GeneratedImage(
                user_id=user_id,
                conversation_id=parent_img_record.conversation_id if parent_img_record else None,
                parent_image_id=parent_id,
                edit_type="upscale_4k",
                provider="super-res",
                model_name="lanczos-4k",
                original_prompt=f"4K Super-Resolution: {orig_prompt}",
                enhanced_prompt=f"4K Upscaled ({new_w}x{new_h}): {orig_prompt}",
                file_path=relative_file_path,
                file_url=new_file_url,
                mime_type="image/png",
                aspect_ratio=f"{new_w}x{new_h}",
                status="completed"
            )
            db.add(new_record)
            await db.commit()
            new_id = new_record.id

        return {
            "id": new_id,
            "file_url": new_file_url,
            "parent_image_id": parent_id,
            "dimensions": f"{new_w}x{new_h}",
            "edit_type": "upscale_4k",
            "status": "completed",
        }

    async def synthesize_edit_prompt(self, original_prompt: str, edit_instruction: str, user_id: int = 1) -> str:
        """
        Uses LLM synthesis to merge original image context with delta edit instruction.
        """
        synthesis_prompt = (
            f"You are an expert AI art director and prompt engineer.\n"
            f"Original Image Description: \"{original_prompt}\"\n"
            f"User Modification: \"{edit_instruction}\"\n\n"
            f"Synthesize a single, vivid, photorealistic image prompt that incorporates the requested changes while preserving the scene subject, style, lighting, and composition of the original.\n"
            f"Output ONLY the synthesized prompt text. No explanations, quotes, or markdown."
        )
        try:
            from app.modules.provider_runtime.manager.provider_runtime_manager import provider_runtime_manager
            res = await provider_runtime_manager.generate_response(
                prompt=synthesis_prompt,
                user_id=user_id,
                temperature=0.2,
                stream=False
            )
            refined = res.get("response", "").strip().strip('"').strip("'")
            if refined and len(refined) > 10:
                return refined
        except Exception as exc:
            logger.warning(f"Edit prompt synthesis fallback to rule-based: {exc}")

        return f"{original_prompt}, modified with {edit_instruction}"


image_generation_service = ImageGenerationService()
