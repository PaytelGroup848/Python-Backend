from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.invoice import (
    Invoice
)


class InvoiceRepository:

    async def create(
        self,
        db: AsyncSession,
        invoice: Invoice
    ):

        try:

            db.add(invoice)

            await db.commit()

            await db.refresh(invoice)

            return invoice

        except Exception:

            await db.rollback()

            raise

    async def get_by_id(
        self,
        db: AsyncSession,
        invoice_id: int
    ):

        result = await db.execute(

            select(Invoice)

            .where(
                Invoice.id == invoice_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_invoice_number(
        self,
        db: AsyncSession,
        invoice_number: str
    ):

        result = await db.execute(

            select(Invoice)

            .where(
                Invoice.invoice_number
                == invoice_number
            )
        )

        return result.scalar_one_or_none()
    
    async def get_latest_invoice(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(Invoice)

            .order_by(
                Invoice.id.desc()
            )

            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(Invoice)

            .where(
                Invoice.user_id == user_id
            )

            .order_by(
                Invoice.created_at.desc()
            )
        )

        return (
            result.scalars()
            .all()
        )
    
    async def get_active_by_user(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(Invoice)

            .where(
                Invoice.user_id == user_id
            )

            .where(
                Invoice.is_active.is_(True)
            )

            .order_by(
                Invoice.created_at.desc()
            )
        )

        return (
            result.scalars()
            .all()
        )
    
    async def get_pending_invoices(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(Invoice)

            .where(
                Invoice.status == "pending"
            )

            .where(
                Invoice.is_active.is_(True)
            )

            .order_by(
                Invoice.created_at.asc()
            )
        )

        return (
            result.scalars()
            .all()
        )

    async def get_by_month(
        self,
        db: AsyncSession,
        billing_month: str
    ):

        result = await db.execute(

            select(Invoice)

            .where(
                Invoice.billing_month
                == billing_month
            )
        )

        return (
            result.scalars()
            .all()
        )
    
    async def get_all(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(
                Invoice
            )

            .order_by(
                Invoice.created_at.desc()
            )
        )

        return (
            result.scalars()
            .all()
        )
    

    async def update(
        self,
        db: AsyncSession,
        invoice: Invoice
    ):

        try:

            await db.commit()

            await db.refresh(invoice)

            return invoice

        except Exception:

            await db.rollback()

            raise


invoice_repository = (
    InvoiceRepository()
)