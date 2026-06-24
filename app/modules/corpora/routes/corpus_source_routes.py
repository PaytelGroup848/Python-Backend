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

from app.modules.corpora.schemas.corpus_source_create import (
    CorpusSourceCreate
)

from app.modules.corpora.services.corpus_source_service import (
    corpus_source_service
)

router = APIRouter(
    prefix="/corpus-sources",
    tags=["Corpus Sources"]
)


@router.post("/")
async def create_source(

    data: CorpusSourceCreate,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        corpus_source_service
        .create_source(
            db,
            data
        )
    )


@router.get("/{source_id}")
async def get_source(

    source_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        corpus_source_service
        .get_source(
            db,
            source_id
        )
    )


@router.get("/corpus/{corpus_id}")
async def get_corpus_sources(

    corpus_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        corpus_source_service
        .get_corpus_sources(
            db,
            corpus_id
        )
    )