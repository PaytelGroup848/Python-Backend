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

from app.core.security import (
    require_role
)

from app.modules.billing.repositories.invoice_repository import (
    invoice_repository
)

router = APIRouter(
    prefix="/admin/invoices",
    tags=["Admin Invoices"]
)


@router.get("")
async def get_invoices(

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    invoices = await (
        invoice_repository
        .get_pending_invoices(
            db
        )
    )

    return {

        "count":
            len(invoices),

        "invoices": [

            {
                "id":
                    invoice.id,

                "invoice_number":
                    invoice.invoice_number,

                "user_id":
                    invoice.user_id,

                "amount":
                    float(invoice.amount),

                "currency":
                    invoice.currency,

                "status":
                    invoice.status,

                "created_at":
                    invoice.created_at
            }

            for invoice
            in invoices
        ]
    }