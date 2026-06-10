from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.wallet_transaction import (
    WalletTransaction
)


class WalletTransactionRepository:

    async def create(
        self,
        db: AsyncSession,
        transaction: WalletTransaction
    ):

        db.add(transaction)

        await db.commit()

        await db.refresh(
            transaction
        )

        return transaction

    async def get_by_id(
        self,
        db: AsyncSession,
        transaction_id: int
    ):

        result = await db.execute(

            select(
                WalletTransaction
            )

            .where(
                WalletTransaction.id
                == transaction_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_by_wallet(
        self,
        db: AsyncSession,
        wallet_id: int,
        limit: int = 100
    ):

        result = await db.execute(

            select(
                WalletTransaction
            )

            .where(
                WalletTransaction.wallet_id
                == wallet_id
            )

            .order_by(
                WalletTransaction.created_at.desc()
            )

            .limit(limit)
        )

        return (
            result.scalars()
            .all()
        )

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 100
    ):

        result = await db.execute(

            select(
                WalletTransaction
            )

            .where(
                WalletTransaction.user_id
                == user_id
            )

            .order_by(
                WalletTransaction.created_at.desc()
            )

            .limit(limit)
        )

        return (
            result.scalars()
            .all()
        )

    async def get_by_reference(
        self,
        db: AsyncSession,
        reference_type: str,
        reference_id: str
    ):

        result = await db.execute(

            select(
                WalletTransaction
            )

            .where(
                WalletTransaction.reference_type
                == reference_type
            )

            .where(
                WalletTransaction.reference_id
                == reference_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_user_transactions_paginated(
        self,
        db: AsyncSession,
        user_id: int,
        offset: int = 0,
        limit: int = 50
    ):

        result = await db.execute(

            select(
                WalletTransaction
            )

            .where(
                WalletTransaction.user_id
                == user_id
            )

            .order_by(
                WalletTransaction.created_at.desc()
            )

            .offset(offset)

            .limit(limit)
        )

        return (
            result.scalars()
            .all()
        )


wallet_transaction_repository = (
    WalletTransactionRepository()
)