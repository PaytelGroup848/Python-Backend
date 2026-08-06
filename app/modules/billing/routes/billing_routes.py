from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException
)
from fastapi.responses import StreamingResponse
from app.modules.billing.services.invoice_data_service import invoice_data_service
from app.modules.billing.services.invoice_pdf_service_v2 import invoice_pdf_service_v2


from slowapi import Limiter


from app.core.security import (
    verify_token
)



from app.modules.billing.services.wallet_service import (
    wallet_service
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.billing.services.billing_service import (
    billing_service
)

from app.modules.billing.services.invoice_service import (
    invoice_service
)

from app.modules.billing.services.subscription_service import (
    subscription_service
)

from app.modules.usage.services.usage_limit_service import (
    usage_limit_service
)
from app.modules.billing.schemas.wallet_schema import (
    WalletCreditRequest
)
router = APIRouter(

    prefix="/billing",

    tags=["Billing"]
)

limiter = Limiter(
    key_func=lambda request:
    request.headers.get(
        "authorization",
        "anonymous"
    )
)


@router.get(
    "/overview"
)
async def billing_overview(

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        billing_service
        .get_billing_overview(
            db
        )
    )

@router.get("/wallet/balance")
@limiter.limit("30/minute")
async def get_wallet_balance(

    request: Request,

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    balance = await (
        wallet_service.get_balance(
            db,
            user["user_id"]
        )
    )

    return {

        "user_id":
            user["user_id"],

        "balance":
            float(balance)
    }
    
@router.get("/wallet/transactions")
@limiter.limit("30/minute")
async def get_transactions(

    request: Request,

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    transactions = await (
        wallet_service
        .transaction_history(

            db,

            user["user_id"]
        )
    )

    return {

        "count":
            len(transactions),

        "transactions": [

            {
                "id":
                    tx.id,

                "transaction_type":
                    tx.transaction_type,

                "amount":
                    float(tx.amount),

                "status":
                    tx.status,

                "balance_before":
                    float(tx.balance_before),

                "balance_after":
                    float(tx.balance_after),

                "reference_type":
                    tx.reference_type,

                "reference_id":
                    tx.reference_id,

                "created_at":
                    tx.created_at
            }

            for tx in transactions
        ]
    }
    
@router.post("/wallet/credit")
@limiter.limit("10/minute")
async def credit_wallet(

    request: Request,

    payload: WalletCreditRequest,

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    wallet = await (
        wallet_service.credit_wallet(

            db=db,

            user_id=user["user_id"],

            amount=payload.amount,

            description="Manual credit"
        )
    )

    return {

        "message":
            "Wallet credited successfully",

        "balance":
                float(
                    wallet.balance
                )
    }

@router.get(
    "/invoices"
)
async def get_user_invoices(

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    invoices = await (
        invoice_service
        .get_user_invoices(
            db,
            user["user_id"]
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

                "invoice_type":
                    invoice.invoice_type,

                "amount":
                    float(invoice.amount),

                "currency":
                    invoice.currency,

                "status":
                    invoice.status,

                "billing_month":
                    invoice.billing_month,

                "created_at":
                    invoice.created_at,

                "due_date":
                    invoice.due_date,

                "paid_at":
                    invoice.paid_at
            }

            for invoice in invoices
        ]
    }

@router.get(
    "/invoices/{invoice_id}"
)
async def get_invoice(

    invoice_id: int,

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    invoice = await (
        invoice_service
        .get_invoice_by_id(
            db,
            invoice_id
        )
    )

    if not invoice:

        raise HTTPException(

            status_code=404,

            detail="Invoice not found"
        )

    if invoice.user_id != user["user_id"]:

        raise HTTPException(

            status_code=403,

            detail="Access denied"
        )

    return {

        "id":
            invoice.id,

        "invoice_number":
            invoice.invoice_number,

        "invoice_type":
            invoice.invoice_type,

        "amount":
            float(invoice.amount),

        "subtotal":
            float(invoice.subtotal),

        "tax_amount":
            float(invoice.tax_amount),

        "currency":
            invoice.currency,

        "status":
            invoice.status,

        "billing_month":
            invoice.billing_month,

        "payment_provider":
            invoice.payment_provider,

        "payment_reference":
            invoice.payment_reference,

        "due_date":
            invoice.due_date,

        "paid_at":
            invoice.paid_at,

        "notes":
            invoice.notes,

        "created_at":
            invoice.created_at
    }

@router.get(
    "/invoices/{invoice_id}/pdf"
)
async def download_user_invoice_pdf(
    invoice_id: int,
    user=Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    invoice_data = await invoice_data_service.build_invoice_data(db, invoice_id)
    if not invoice_data or not invoice_data.get("invoice"):
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice = invoice_data["invoice"]
    if invoice.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    pdf_buffer = await invoice_pdf_service_v2.generate(invoice_data)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"
        }
    )


@router.get(
    "/subscription"
)
async def get_subscription(

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    subscription = await (
        subscription_service
        .get_user_subscription(
            db,
            user["user_id"]
        )
    )

    if not subscription:

        return {
            "subscription": None
        }

    return {

        "id":
            subscription.id,

        "plan_name":
            subscription.plan_name,

        "status":
            subscription.status,

        "monthly_token_limit":
            subscription.monthly_token_limit,

        "auto_renew":
            subscription.auto_renew,

        "start_date":
            subscription.start_date,

        "end_date":
            subscription.end_date
    }

@router.post(
    "/subscription/cancel"
)
async def cancel_subscription(

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    success = await (
        subscription_service
        .cancel_subscription(
            db,
            user["user_id"]
        )
    )

    if not success:

        raise HTTPException(

            status_code=404,

            detail="No active subscription found"
        )

    return {

        "message":
            "Subscription cancelled"
    }

@router.post(
    "/subscription/renew"
)
async def renew_subscription(

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    subscription = await (
        subscription_service
        .renew_subscription(
            db,
            user["user_id"]
        )
    )

    if not subscription:

        raise HTTPException(

            status_code=404,

            detail="No active subscription found"
        )

    return {

        "message":
            "Subscription renewed",

        "end_date":
            subscription.end_date
    }

@router.get(
    "/limits"
)
async def get_limits(

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    plan = await (
        usage_limit_service
        .get_user_plan(
            db,
            user["user_id"]
        )
    )

    limits = await (
        usage_limit_service
        .get_user_limits(
            db,
            user["user_id"]
        )
    )

    return {

        "plan":
            plan,

        "monthly_token_limit":
            limits.monthly_token_limit,

        "monthly_request_limit":
            limits.monthly_request_limit,

        "monthly_cost_limit":
            limits.monthly_cost_limit
    }

@router.get(
    "/usage"
)
async def get_usage(

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        usage_limit_service
        .get_usage_summary(
            db,
            user["user_id"]
        )
    )