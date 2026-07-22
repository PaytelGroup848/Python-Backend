from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import (
    get_db,
)

from app.modules.tokenizers.services.tokenizer_service import (
    tokenizer_service,
)

from app.modules.tokenizers.services.tokenizer_version_service import (
    tokenizer_version_service,
)

router = APIRouter(

    prefix="/tokenizers",

    tags=[
        "Tokenizers",
    ],

)

# =====================================
# List Tokenizers
# =====================================

@router.get("")
async def list_tokenizers(

    db: AsyncSession = Depends(
        get_db,
    ),

):

    return await (

        tokenizer_service
        .list_tokenizers(

            db=db,

        )

    )

# =====================================
# Get Tokenizer
# =====================================

@router.get(
    "/{tokenizer_id}",
)
async def get_tokenizer(

    tokenizer_id: int,

    db: AsyncSession = Depends(
        get_db,
    ),

):

    tokenizer = await (

        tokenizer_service
        .get_by_id(

            db=db,

            tokenizer_id=tokenizer_id,

        )

    )

    if tokenizer is None:

        raise HTTPException(

            status_code=404,

            detail="Tokenizer not found",

        )

    return tokenizer

# =====================================
# List Tokenizer Versions
# =====================================

@router.get(
    "/{tokenizer_id}/versions",
)
async def list_tokenizer_versions(

    tokenizer_id: int,

    db: AsyncSession = Depends(
        get_db,
    ),

):

    return await (

        tokenizer_version_service
        .list_by_tokenizer(

            db=db,

            tokenizer_id=tokenizer_id,

        )

    )

# =====================================
# Get Tokenizer Version
# =====================================

@router.get(
    "/versions/{tokenizer_version_id}",
)
async def get_tokenizer_version(

    tokenizer_version_id: int,

    db: AsyncSession = Depends(
        get_db,
    ),

):

    tokenizer_version = await (

        tokenizer_version_service
        .get_by_id(

            db=db,

            tokenizer_version_id=tokenizer_version_id,

        )

    )

    if tokenizer_version is None:

        raise HTTPException(

            status_code=404,

            detail="Tokenizer version not found",

        )

    return tokenizer_version