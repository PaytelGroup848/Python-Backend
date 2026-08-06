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
    verify_token,
    require_role,
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
        verify_token
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

    if not invoice_data or not invoice_data.get("invoice"):
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    invoice = (
        invoice_data["invoice"]
    )

    user_id = user.get("user_id") if isinstance(user, dict) else getattr(user, "id", None)
    user_role = user.get("role") if isinstance(user, dict) else getattr(user, "role", None)

    if invoice.user_id != user_id and user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied to this invoice"
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