import logging
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.image_generation_service import image_generation_service

logger = logging.getLogger("media_routes")

router = APIRouter(prefix="/api/v1/media", tags=["Media Studio"])


class RemoveBgRequest(BaseModel):
    image_id: Optional[int] = None
    file_url: Optional[str] = None


class UpscaleRequest(BaseModel):
    image_id: Optional[int] = None
    file_url: Optional[str] = None
    scale: int = 4


class ImageEditRequest(BaseModel):
    prompt: str
    parent_image_id: Optional[int] = None
    conversation_id: Optional[int] = None
    aspect_ratio: str = "1024x1024"


@router.post("/remove-bg")
async def remove_background_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    1-Click Background Removal endpoint.
    Accepts JSON with image_id or file_url, OR multipart/form-data upload.
    Returns the transparent PNG asset URL.
    """
    raw_bytes = None
    image_id = None
    file_url = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            image_id = body.get("image_id")
            file_url = body.get("file_url")
        except Exception:
            pass
    elif "multipart/form-data" in content_type:
        form = await request.form()
        image_id = form.get("image_id")
        file_url = form.get("file_url")
        uploaded_file = form.get("file")
        if uploaded_file and hasattr(uploaded_file, "read"):
            raw_bytes = await uploaded_file.read()
    else:
        try:
            body = await request.json()
            image_id = body.get("image_id")
            file_url = body.get("file_url")
        except Exception:
            pass

    if image_id and isinstance(image_id, str) and image_id.isdigit():
        image_id = int(image_id)

    if not raw_bytes and not image_id and not file_url:
        raise HTTPException(
            status_code=400,
            detail="Either 'image_id', 'file_url', or uploaded file must be provided."
        )

    try:
        result = await image_generation_service.remove_background(
            user_id=current_user.id,
            image_id=image_id,
            file_url=file_url,
            raw_image_bytes=raw_bytes,
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as exc:
        logger.error(f"Background removal failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Background removal failed: {str(exc)}")


@router.post("/upscale")
async def upscale_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    AI 4K Super-Resolution endpoint.
    Accepts JSON with image_id or file_url, OR multipart/form-data upload.
    Returns 4x enhanced high-definition asset.
    """
    raw_bytes = None
    image_id = None
    file_url = None
    target_scale = 4

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            image_id = body.get("image_id")
            file_url = body.get("file_url")
            target_scale = int(body.get("scale", 4))
        except Exception:
            pass
    elif "multipart/form-data" in content_type:
        form = await request.form()
        image_id = form.get("image_id")
        file_url = form.get("file_url")
        target_scale = int(form.get("scale", 4))
        uploaded_file = form.get("file")
        if uploaded_file and hasattr(uploaded_file, "read"):
            raw_bytes = await uploaded_file.read()
    else:
        try:
            body = await request.json()
            image_id = body.get("image_id")
            file_url = body.get("file_url")
            target_scale = int(body.get("scale", 4))
        except Exception:
            pass

    if image_id and isinstance(image_id, str) and image_id.isdigit():
        image_id = int(image_id)

    if not raw_bytes and not image_id and not file_url:
        raise HTTPException(
            status_code=400,
            detail="Either 'image_id', 'file_url', or uploaded file must be provided."
        )

    try:
        result = await image_generation_service.upscale_image(
            user_id=current_user.id,
            image_id=image_id,
            file_url=file_url,
            raw_image_bytes=raw_bytes,
            scale=target_scale or 4,
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as exc:
        logger.error(f"Image upscaling failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Image upscaling failed: {str(exc)}")


@router.post("/edit")
async def edit_image_endpoint(
    request: ImageEditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Conversational Image Editing endpoint.
    Applies edit prompt to parent image while maintaining composition.
    """
    from sqlalchemy import select
    from app.models.generated_image import GeneratedImage

    parent_prompt = ""
    parent_id = request.parent_image_id

    if parent_id:
        p_res = await db.execute(select(GeneratedImage).filter(GeneratedImage.id == parent_id))
        parent_rec = p_res.scalar_one_or_none()
        if parent_rec:
            parent_prompt = parent_rec.original_prompt
    elif request.conversation_id:
        p_res = await db.execute(
            select(GeneratedImage)
            .filter(GeneratedImage.conversation_id == request.conversation_id, GeneratedImage.status == "completed")
            .order_by(GeneratedImage.id.desc())
            .limit(1)
        )
        parent_rec = p_res.scalar_one_or_none()
        if parent_rec:
            parent_id = parent_rec.id
            parent_prompt = parent_rec.original_prompt

    if parent_prompt:
        synthesized_prompt = await image_generation_service.synthesize_edit_prompt(
            original_prompt=parent_prompt,
            edit_instruction=request.prompt,
            user_id=current_user.id
        )
    else:
        synthesized_prompt = request.prompt

    try:
        result = await image_generation_service.generate_and_persist(
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            prompt=synthesized_prompt,
            aspect_ratio=request.aspect_ratio,
            parent_image_id=parent_id,
            edit_type="edit" if parent_id else "generation",
        )
        return {
            "success": True,
            "data": result,
            "parent_image_id": parent_id,
            "synthesized_prompt": synthesized_prompt
        }
    except Exception as exc:
        logger.error(f"Image edit failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Image edit failed: {str(exc)}")
