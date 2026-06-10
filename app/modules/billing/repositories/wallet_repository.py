from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.wallet import (
    Wallet
)


class WalletRepository:

    async def create(
        self,
        db: AsyncSession,
        wallet: Wallet
    ):

        db.add(wallet)

        await db.commit()

        await db.refresh(wallet)

        return wallet

    async def get_by_id(
        self,
        db: AsyncSession,
        wallet_id: int
    ):

        result = await db.execute(

            select(Wallet)

            .where(
                Wallet.id == wallet_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(Wallet)

            .where(
                Wallet.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_for_update(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(Wallet)

            .where(
                Wallet.user_id == user_id
            )

            .with_for_update()
        )

        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        db: AsyncSession,
        user_id: int
    ):

        wallet = await self.get_by_user_id(
            db,
            user_id
        )

        if wallet:

            return wallet

        wallet = Wallet(
            user_id=user_id,
            balance=0
        )

        db.add(wallet)

        await db.commit()

        await db.refresh(wallet)

        return wallet

    async def update(
        self,
        db: AsyncSession,
        wallet: Wallet
    ):

        await db.commit()

        await db.refresh(wallet)

        return wallet


wallet_repository = (
    WalletRepository()
)