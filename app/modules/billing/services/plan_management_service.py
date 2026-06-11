from decimal import Decimal

from app.modules.billing.services.plan_service import (
    plan_service
)

from app.modules.billing.repositories.plan_repository import (
    plan_repository
)

from app.modules.billing.repositories.plan_version_repository import (
    plan_version_repository
)

from app.modules.billing.repositories.plan_price_repository import (
    plan_price_repository
)


class PlanManagementService:

    async def create_plan(
        self,
        db,
        plan_code: str,
        plan_name: str,
        description: str = None,
        is_public: bool = True
    ):

        return await (
            plan_service.create_plan(
                db=db,
                plan_code=plan_code,
                plan_name=plan_name,
                description=description,
                is_public=is_public
            )
        )

    async def create_plan_version(
        self,
        db,
        plan_id: int,
        version_number: int,
        monthly_token_limit: int,
        monthly_request_limit: int,
        monthly_cost_limit: int = None
    ):

        current_version = await (
            plan_version_repository
            .get_active_by_plan(
                db,
                plan_id
            )
        )

        if current_version:

            current_version.is_active = False

            await (
                plan_version_repository
                .update(
                    db,
                    current_version
                )
            )

        return await (
            plan_service
            .create_plan_version(
                db=db,
                plan_id=plan_id,
                version_number=version_number,
                monthly_token_limit=monthly_token_limit,
                monthly_request_limit=monthly_request_limit,
                monthly_cost_limit=monthly_cost_limit
            )
        )

    async def create_plan_price(
        self,
        db,
        plan_version_id: int,
        provider: str,
        currency: str,
        amount: Decimal,
        billing_cycle: str,
        external_price_id: str = None
    ):

        return await (
            plan_service
            .create_plan_price(
                db=db,
                plan_version_id=plan_version_id,
                provider=provider,
                currency=currency,
                amount=amount,
                billing_cycle=billing_cycle,
                external_price_id=external_price_id
            )
        )

    async def deactivate_plan(
        self,
        db,
        plan_id: int
    ):

        plan = await (
            plan_repository
            .get_by_id(
                db,
                plan_id
            )
        )

        if not plan:

            return None

        plan.is_active = False

        return await (
            plan_repository
            .update(
                db,
                plan
            )
        )

    async def deactivate_plan_price(
        self,
        db,
        price_id: int
    ):

        price = await (
            plan_price_repository
            .get_by_id(
                db,
                price_id
            )
        )

        if not price:

            return None

        price.is_active = False

        return await (
            plan_price_repository
            .update(
                db,
                price
            )
        )


plan_management_service = (
    PlanManagementService()
)