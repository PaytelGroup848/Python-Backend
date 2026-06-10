from decimal import Decimal

from datetime import (
    datetime,
    timedelta
)

from app.modules.billing.models.invoice import (
    Invoice
)

from app.modules.billing.repositories.invoice_repository import (
    invoice_repository
)


class InvoiceService:

    async def generate_invoice_number(
        self,
        db
    ):

        latest_invoice = await (
            invoice_repository
            .get_latest_invoice(db)
        )

        current_month = (
            datetime.utcnow()
            .strftime("%Y%m")
        )

        next_number = 1

        if latest_invoice:

            next_number = (
                latest_invoice.id + 1
            )

        return (
            f"INV-{current_month}-"
            f"{str(next_number).zfill(6)}"
        )

    async def create_subscription_invoice(
        self,
        db,
        user_id: int,
        subscription_id: int,
        amount: Decimal,
        currency: str,
        auto_renew: bool = False,
        notes: str = None
    ):

        invoice_number = await (
            self.generate_invoice_number(
                db
            )
        )

        now = datetime.utcnow()

        invoice = Invoice(

            user_id=user_id,

            subscription_id=
                subscription_id,

            invoice_number=
                invoice_number,

            invoice_type=
                "subscription",

            subtotal=
                amount,

            tax_amount=
                Decimal("0"),

            amount=
                amount,

            currency=
                currency,

            status=
                "pending",

            billing_month=
                now.strftime("%Y-%m"),

            auto_renew=
                auto_renew,

            due_date=
                now + timedelta(days=7),

            notes=
                notes
        )

        return await (
            invoice_repository
            .create(
                db,
                invoice
            )
        )

    async def create_usage_invoice(
        self,
        db,
        user_id: int,
        amount: Decimal,
        currency: str,
        notes: str = None
    ):

        invoice_number = await (
            self.generate_invoice_number(
                db
            )
        )

        now = datetime.utcnow()

        invoice = Invoice(

            user_id=user_id,

            invoice_number=
                invoice_number,

            invoice_type=
                "usage",

            subtotal=
                amount,

            tax_amount=
                Decimal("0"),

            amount=
                amount,

            currency=
                currency,

            status=
                "pending",

            billing_month=
                now.strftime("%Y-%m"),

            due_date=
                now + timedelta(days=7),

            notes=
                notes
        )

        return await (
            invoice_repository
            .create(
                db,
                invoice
            )
        )

    async def mark_paid(
        self,
        db,
        invoice_id: int,
        payment_provider: str,
        payment_reference: str
    ):

        invoice = await (
            invoice_repository
            .get_by_id(
                db,
                invoice_id
            )
        )

        if not invoice:

            return None

        invoice.status = "paid"

        invoice.paid_at = (
            datetime.utcnow()
        )

        invoice.payment_provider = (
            payment_provider
        )

        invoice.payment_reference = (
            payment_reference
        )

        return await (
            invoice_repository
            .update(
                db,
                invoice
            )
        )

    async def mark_failed(
        self,
        db,
        invoice_id: int,
        notes: str = None
    ):

        invoice = await (
            invoice_repository
            .get_by_id(
                db,
                invoice_id
            )
        )

        if not invoice:

            return None

        invoice.status = "failed"

        if notes:

            invoice.notes = notes

        return await (
            invoice_repository
            .update(
                db,
                invoice
            )
        )

    async def cancel_invoice(
        self,
        db,
        invoice_id: int,
        notes: str = None
    ):

        invoice = await (
            invoice_repository
            .get_by_id(
                db,
                invoice_id
            )
        )

        if not invoice:

            return None

        invoice.status = "cancelled"

        invoice.is_active = False

        if notes:

            invoice.notes = notes

        return await (
            invoice_repository
            .update(
                db,
                invoice
            )
        )

    async def get_user_invoices(
        self,
        db,
        user_id: int
    ):

        return await (
            invoice_repository
            .get_active_by_user(
                db,
                user_id
            )
        )
    
    async def get_invoice_by_id(
        self,
        db,
        invoice_id: int
    ):

        return await (
            invoice_repository
            .get_by_id(
                db,
                invoice_id
            )
        )
    
    async def get_pending_invoices(
        self,
        db
    ):

        return await (
            invoice_repository
            .get_pending_invoices(
                db
            )
        )


invoice_service = (
    InvoiceService()
)