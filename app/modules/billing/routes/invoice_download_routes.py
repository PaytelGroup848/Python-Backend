from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.responses import (
    StreamingResponse
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.core.security import (
    require_role
)

from app.modules.billing.services.invoice_data_service import (
    invoice_data_service
)

from app.modules.billing.services.invoice_pdf_service_v2 import (
    invoice_pdf_service_v2
)

router = APIRouter(

    prefix="/admin/invoices",

    tags=["Admin Invoices"]
)


@router.get(
    "/{invoice_id}/pdf"
)
async def download_invoice_pdf(

    invoice_id: int,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    invoice_data = await (
        invoice_data_service
        .build_invoice_data(
            db,
            invoice_id
        )
    )

    if not invoice_data:

        raise HTTPException(

            status_code=404,

            detail="Invoice not found"
        )

    pdf_buffer = await (
        invoice_pdf_service_v2
        .generate(
            invoice_data
        )
    )

    invoice = (
        invoice_data["invoice"]
    )

    return StreamingResponse(

        pdf_buffer,

        media_type=
            "application/pdf",

        headers={
            "Content-Disposition":
            (
                f"attachment;"
                f" filename="
                f"{invoice.invoice_number}.pdf"
            )
        }
    )