from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.corpora.schemas.corpus_create import (
    CorpusCreate
)

from app.modules.corpora.services.corpus_service import (
    corpus_service
)

router = APIRouter(
    prefix="/corpora",
    tags=["Corpora"]
)


@router.post("/")
async def create_corpus(

    data: CorpusCreate,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        corpus_service
        .create_corpus(
            db,
            data
        )
    )


@router.get("/{corpus_id}")
async def get_corpus(

    corpus_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        corpus_service
        .get_corpus(
            db,
            corpus_id
        )
    )


@router.get("/")
async def list_corpora(

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        corpus_service
        .list_corpora(
            db
        )
    )