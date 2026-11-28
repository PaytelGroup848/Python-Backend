from __future__ import annotations

import logging
import re
from typing import Optional

from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.generated_image import GeneratedImage
from app.modules.memory.services.memory_service import memory_service
from app.services.agent.schemas import AgentState, IntentType, StreamHandler
from app.services.image_generation_service import image_generation_service
from app.services.image_providers.base import ContentPolicyViolationError

logger = logging.getLogger("enterprise_agent")

_BG_REMOVE_TERMS = ("remove background", "remove bg", "transparent background", "background remove", "bg hatao")
_UPSCALE_TERMS = ("upscale", "4k", "super resolution", "enhance resolution")
_EDIT_HINTS = ("change", "make the", "turn the", "add ", "remove ", "replace ", "edit ", "modify ", "isme ")


def _parse_aspect_ratio(query: str, requested_ratio: Optional[str]) -> tuple[str, str]:
    clean_prompt = query
    q_lower = query.lower()

    if any(k in q_lower for k in ("--ar 16:9", "16:9", "landscape", "widescreen")):
        return "1280x720", re.sub(r"--ar\s+16:9", "", clean_prompt, flags=re.IGNORECASE).strip()
    if any(k in q_lower for k in ("--ar 9:16", "9:16", "portrait", "vertical")):
        return "720x1280", re.sub(r"--ar\s+9:16", "", clean_prompt, flags=re.IGNORECASE).strip()
    if any(k in q_lower for k in ("--ar 1:1", "1:1", "square")):
        return "1024x1024", re.sub(r"--ar\s+1:1", "", clean_prompt, flags=re.IGNORECASE).strip()

    if requested_ratio in ("16:9", "1280x720"):
        return "1280x720", clean_prompt
    if requested_ratio in ("9:16", "720x1280"):
        return "720x1280", clean_prompt
    return "1024x1024", clean_prompt


async def _find_parent_image(conv_id: Optional[int], user_id: int) -> Optional[GeneratedImage]:
    try:
        async with AsyncSessionLocal() as db:
            if conv_id:
                res = await db.execute(
                    select(GeneratedImage)
                    .filter(GeneratedImage.conversation_id == conv_id, GeneratedImage.status == "completed")
                    .order_by(GeneratedImage.id.desc())
                    .limit(1)
                )
                found = res.scalar_one_or_none()
                if found:
                    return found
            if user_id:
                res = await db.execute(
                    select(GeneratedImage)
                    .filter(GeneratedImage.user_id == user_id, GeneratedImage.status == "completed")
                    .order_by(GeneratedImage.id.desc())
                    .limit(1)
                )
                return res.scalar_one_or_none()
    except Exception as exc:
        logger.warning(f"Parent image lookup error: {exc}")
    return None


async def _try_quick_edit(
    state: AgentState,
    parent_image: GeneratedImage,
    user_id: int,
    q_lower: str,
) -> Optional[dict]:
    if any(bg in q_lower for bg in _BG_REMOVE_TERMS):
        try:
            bg_result = await image_generation_service.remove_background(user_id=user_id, image_id=parent_image.id)
            bg_url = bg_result["file_url"]
            return {
                **state,
                "response": f"![Transparent Cutout]({bg_url})\n\n**1-Click Background Removed:** Transparent PNG cutout ready for download or presentation.",
                "metadata": {**state.get("metadata", {}), "image_url": bg_url, "edit_type": "remove_bg"},
            }
        except Exception as exc:
            logger.error(f"Chat background removal failed: {exc}")

    if any(up in q_lower for up in _UPSCALE_TERMS):
        try:
            up_result = await image_generation_service.upscale_image(user_id=user_id, image_id=parent_image.id, scale=4)
            up_url = up_result["file_url"]
            dims = up_result.get("dimensions", "4096x4096")
            return {
                **state,
                "response": f"![4K Ultra HD]({up_url})\n\n**AI 4K Super-Resolution Enhanced ({dims}):** 4x ultra-crisp resolution ready for download.",
                "metadata": {**state.get("metadata", {}), "image_url": up_url, "edit_type": "upscale_4k"},
            }
        except Exception as exc:
            logger.error(f"Chat upscale failed: {exc}")

    return None


async def _emit_stage(stream_handler: Optional[StreamHandler], stage: str, message: str) -> None:
    if stream_handler is None:
        return
    try:
        await stream_handler({"type": "stage", "stage": stage, "message": message})
    except Exception:
        pass


async def _save_image_memory(state: AgentState, response_md: str) -> None:
    if not state.get("memory_enabled") or not state.get("session_id"):
        return
    try:
        await memory_service.save_memory(session_id=state["session_id"], role="user", message=state["query"])
        await memory_service.save_memory(session_id=state["session_id"], role="assistant", message=response_md)
    except Exception as exc:
        logger.warning(f"Failed to save image memory: {exc}")


async def image_gen_node(state: AgentState):
    """Handles image generation, conversational edits, background removal, and 4K upscaling."""
    user_id = state.get("user_id") or 1
    session_id_raw = state.get("session_id")
    conv_id = int(session_id_raw) if session_id_raw and str(session_id_raw).isdigit() else None
    query = state.get("query", "")
    q_lower = query.lower()

    aspect_ratio_param, clean_prompt = _parse_aspect_ratio(query, state.get("aspect_ratio"))
    parent_image = await _find_parent_image(conv_id, user_id)

    if parent_image:
        quick_result = await _try_quick_edit(state, parent_image, user_id, q_lower)
        if quick_result is not None:
            return quick_result

    is_edit = False
    parent_id = None
    target_prompt = clean_prompt or query
    if parent_image and (
        state.get("intent") == IntentType.IMAGE_EDIT.value
        or any(w in q_lower for w in _EDIT_HINTS)
    ):
        logger.info(f"Conversational image edit detected! Parent #{parent_image.id}: '{parent_image.original_prompt}'")
        target_prompt = await image_generation_service.synthesize_edit_prompt(
            original_prompt=parent_image.original_prompt,
            edit_instruction=clean_prompt or query,
            user_id=user_id,
        )
        parent_id = parent_image.id
        is_edit = True
        if aspect_ratio_param == "1024x1024" and parent_image.aspect_ratio:
            aspect_ratio_param = parent_image.aspect_ratio

    stream_handler = state.get("stream_handler")
    await _emit_stage(stream_handler, "generating", "Synthesizing artwork...")

    try:
        result = await image_generation_service.generate_and_persist(
            user_id=user_id,
            conversation_id=conv_id,
            prompt=target_prompt,
            aspect_ratio=aspect_ratio_param,
            parent_image_id=parent_id,
            edit_type="edit" if is_edit else "generation",
        )
        file_url = result["file_url"]
        ar_labels = {"1280x720": "16:9 Widescreen", "720x1280": "9:16 Portrait"}
        ar_display = ar_labels.get(aspect_ratio_param, "1:1 Square")

        if is_edit and parent_image:
            response_md = f"![{target_prompt}]({file_url})\n\n**Edited Artwork (v2):** *\"{target_prompt}\"* ({ar_display})\n*✨ Modified from: \"{parent_image.original_prompt}\"*"
        else:
            response_md = f"![{clean_prompt or query}]({file_url})\n\n**Generated Artwork:** *\"{clean_prompt or query}\"* ({ar_display})"

        await _emit_stage(stream_handler, "completed", "Artwork generated")
        await _save_image_memory(state, response_md)

        return {
            **state,
            "response": response_md,
            "metadata": {
                **state.get("metadata", {}),
                "image_url": file_url,
                "provider": result.get("provider"),
                "model_name": result.get("model_name"),
            },
        }
    except ContentPolicyViolationError as cpv:
        return {
            **state,
            "response": f"⚠️ **Content Policy Violation**: {str(cpv)}\nYour prompt could not be processed, and no credits were deducted.",
        }
    except Exception as exc:
        logger.error(f"Image generation node failure: {exc}")
        return {
            **state,
            "response": f"⚠️ **Image Generation Failed**: {str(exc)}\nPlease try again. Any reserved credits have been restored.",
        }
