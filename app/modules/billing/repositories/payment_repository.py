from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.payment import (
    Payment
)


class PaymentRepository:

    async def create(
        self,
        db: AsyncSession,
        payment: Payment
    ):

        try:

            db.add(payment)

            await db.commit()

            await db.refresh(payment)

            return payment

        except Exception:

            await db.rollback()

            raise

    async def get_by_id(
        self,
        db: AsyncSession,
        payment_id: int
    ):

        result = await db.execute(

            select(Payment)

            .where(
                Payment.id == payment_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_gateway_payment_id(
        self,
        db: AsyncSession,
        gateway_payment_id: str
    ):

        result = await db.execute(

            select(Payment)

            .where(
                Payment.gateway_payment_id
                == gateway_payment_id
            )
        )

        return result.scalar_one_or_none()
    
    async def get_by_gateway_order_id(
        self,
        db: AsyncSession,
        gateway_order_id: str
    ):

        result = await db.execute(

            select(Payment)

            .where(
                Payment.gateway_order_id
                == gateway_order_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(Payment)

            .where(
                Payment.user_id == user_id
            )

            .order_by(
                Payment.created_at.desc()
            )
        )

        return (
            result.scalars()
            .all()
        )

    async def update(
        self,
        db: AsyncSession,
        payment: Payment
    ):

        try:

            await db.commit()

            await db.refresh(payment)

            return payment

        except Exception:

            await db.rollback()

            raise


payment_repository = (
    PaymentRepository()
)