from decimal import Decimal
from fastapi import HTTPException
from datetime import datetime


from app.modules.billing.models.wallet import (
    Wallet
)

from app.modules.billing.models.wallet_transaction import (
    WalletTransaction
)

from app.modules.billing.repositories.wallet_repository import (
    wallet_repository
)

from app.modules.billing.repositories.wallet_transaction_repository import (
    wallet_transaction_repository
)


class WalletService:

    async def create_wallet(
        self,
        db,
        user_id: int
    ):

        wallet = await (
            wallet_repository.get_by_user_id(
                db,
                user_id
            )
        )

        if wallet:

            return wallet

        wallet = Wallet(
            user_id=user_id,
            balance=Decimal("0")
        )

        return await (
            wallet_repository.create(
                db,
                wallet
            )
        )

    async def get_balance(
        self,
        db,
        user_id: int
    ):

        wallet = await (
            wallet_repository.get_or_create(
                db,
                user_id
            )
        )

        return wallet.balance

    async def credit_wallet(
        self,
        db,
        user_id: int,
        amount: Decimal,
        description: str,
        reference_type: str = None,
        reference_id: str = None
    ):

        wallet = await (
            wallet_repository.get_for_update(
                db,
                user_id
            )
        )

        if not wallet:

            wallet = await (
                self.create_wallet(
                    db,
                    user_id
                )
            )

            wallet = await (
                wallet_repository.get_for_update(
                    db,
                    user_id
                )
            )

        balance_before = Decimal(
            str(wallet.balance)
        )

        balance_after = (
            balance_before
            + amount
        )

        try:

            wallet.balance = balance_after

            wallet.updated_at = datetime.utcnow()

            transaction = WalletTransaction(

                wallet_id=wallet.id,

                user_id=user_id,

                transaction_type="credit",

                status="completed",

                amount=amount,

                balance_before=balance_before,

                balance_after=balance_after,

                reference_type=reference_type,

                reference_id=reference_id,

                description=description
            )

            db.add(transaction)

            await db.commit()

            await db.refresh(wallet)

        except Exception:

            await db.rollback()

            raise

        return wallet

    async def debit_wallet(
        self,
        db,
        user_id: int,
        amount: Decimal,
        description: str,
        reference_type: str = None,
        reference_id: str = None
    ):

        wallet = await (
            wallet_repository.get_for_update(
                db,
                user_id
            )
        )

        if not wallet:

            raise HTTPException(
                status_code=404,
                detail="Wallet not found"
            )

        balance_before = Decimal(
            str(wallet.balance)
        )

        if balance_before < amount:

            raise HTTPException(
                status_code=402,
                detail="Insufficient wallet balance"
            )

        balance_after = (
            balance_before
            - amount
        )

        try:

            wallet.balance = balance_after

            wallet.updated_at = datetime.utcnow()

            transaction = WalletTransaction(

                wallet_id=wallet.id,

                user_id=user_id,

                transaction_type="debit",

                status="completed",

                amount=amount,

                balance_before=balance_before,

                balance_after=balance_after,

                reference_type=reference_type,

                reference_id=reference_id,

                description=description
            )

            db.add(transaction)

            await db.commit()

            await db.refresh(wallet)

        except Exception:

            await db.rollback()

            raise
        return wallet

    async def transaction_history(
        self,
        db,
        user_id: int,
        limit: int = 100
    ):

        return await (
            wallet_transaction_repository
            .get_by_user(
                db,
                user_id,
                limit
            )
        )


wallet_service = (
    WalletService()
)