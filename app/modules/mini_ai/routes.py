from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db
from app.modules.mini_ai.entitlements import MiniAIEntitlements, get_mini_ai_entitlements
from app.modules.mini_ai.schemas import (
    MiniAIDocumentsResponse,
    MiniAIInsightsResponse,
    MiniAIResponse,
    MiniAIUpdateRequest,
    TrainGapRequest,
)
from app.modules.mini_ai.service import mini_ai_service

router = APIRouter(
    prefix="/mini-ai",
    tags=["My Mini AI"],
)


@router.post(
    "",
    response_model=MiniAIResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/",
    response_model=MiniAIResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_mini_ai(
    name: str = Form(...),
    system_prompt: str = Form(...),
    description: str | None = Form(None),
    qa_pairs: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await mini_ai_service.create_mini_ai(
            db=db,
            user_id=current_user.id,
            name=name,
            system_prompt=system_prompt,
            description=description,
            qa_pairs_json=qa_pairs,
            upload_file=file,
        )
        await db.commit()
        return result
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Mini AI: {exc}",
        )


@router.get("/entitlements", response_model=MiniAIEntitlements)
async def get_my_mini_ai_entitlements(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_mini_ai_entitlements(db=db, user_id=current_user.id)


@router.get("", response_model=list[MiniAIResponse])
@router.get("/", response_model=list[MiniAIResponse])
async def list_mini_ais(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await mini_ai_service.list_mini_ais(db=db, user_id=current_user.id)


@router.post("/{mini_ai_id}/knowledge", response_model=MiniAIResponse)
async def add_mini_ai_knowledge(
    mini_ai_id: int,
    qa_pairs: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await mini_ai_service.add_knowledge(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=current_user.id,
            qa_pairs_json=qa_pairs,
            upload_file=file,
        )
        await db.commit()
        return result
    except LookupError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add knowledge: {exc}",
        )


@router.patch("/{mini_ai_id}", response_model=MiniAIResponse)
async def update_mini_ai(
    mini_ai_id: int,
    payload: MiniAIUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await mini_ai_service.update_mini_ai(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=current_user.id,
            payload=payload,
        )
        await db.commit()
        return result
    except LookupError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{mini_ai_id}/documents", response_model=MiniAIDocumentsResponse)
async def list_mini_ai_documents(
    mini_ai_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return await mini_ai_service.list_documents(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=current_user.id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{mini_ai_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mini_ai_document(
    mini_ai_id: int,
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        await mini_ai_service.delete_document(
            db=db,
            mini_ai_id=mini_ai_id,
            doc_id=doc_id,
            user_id=current_user.id,
        )
        await db.commit()
    except LookupError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{mini_ai_id}/insights", response_model=MiniAIInsightsResponse)
async def get_mini_ai_insights(
    mini_ai_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return await mini_ai_service.get_insights(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/{mini_ai_id}/gaps/{gap_id}/train", response_model=MiniAIResponse)
async def train_mini_ai_gap(
    mini_ai_id: int,
    gap_id: int,
    payload: TrainGapRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await mini_ai_service.train_gap(
            db=db,
            mini_ai_id=mini_ai_id,
            gap_id=gap_id,
            user_id=current_user.id,
            answer=payload.answer,
        )
        await db.commit()
        return result
    except LookupError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add knowledge: {exc}",
        )


@router.delete("/{mini_ai_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mini_ai(
    mini_ai_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        await mini_ai_service.delete_mini_ai(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=current_user.id,
        )
        await db.commit()
    except LookupError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/{mini_ai_id}", response_model=MiniAIResponse)
async def update_mini_ai(
    mini_ai_id: int,
    payload: MiniAIUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await mini_ai_service.update_mini_ai(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=current_user.id,
            payload=payload,
        )
        await db.commit()
        return result
    except LookupError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{mini_ai_id}/documents", response_model=MiniAIDocumentsResponse)
async def list_mini_ai_documents(
    mini_ai_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return await mini_ai_service.list_documents(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=current_user.id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{mini_ai_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mini_ai_document(
    mini_ai_id: int,
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        await mini_ai_service.delete_document(
            db=db,
            mini_ai_id=mini_ai_id,
            doc_id=doc_id,
            user_id=current_user.id,
        )
        await db.commit()
    except LookupError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{mini_ai_id}/insights", response_model=MiniAIInsightsResponse)
async def get_mini_ai_insights(
    mini_ai_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return await mini_ai_service.get_insights(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/{mini_ai_id}/gaps/{gap_id}/train", response_model=MiniAIResponse)
async def train_mini_ai_gap(
    mini_ai_id: int,
    gap_id: int,
    payload: TrainGapRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = await mini_ai_service.train_gap(
            db=db,
            mini_ai_id=mini_ai_id,
            gap_id=gap_id,
            user_id=current_user.id,
            answer=payload.answer,
        )
        await db.commit()
        return result
    except LookupError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
