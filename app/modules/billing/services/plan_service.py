from app.modules.billing.models.plan import (
    Plan
)

from app.modules.billing.models.plan_version import (
    PlanVersion
)

from app.modules.billing.models.plan_price import (
    PlanPrice
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


class PlanService:

    async def create_plan(
        self,
        db,
        plan_code: str,
        plan_name: str,
        description: str = None,
        is_public: bool = True
    ):

        existing_plan = await (
            plan_repository
            .get_by_code(
                db,
                plan_code
            )
        )

        if existing_plan:

            raise ValueError(
                f"Plan '{plan_code}' already exists"
            )

        plan = Plan(

            plan_code=plan_code,

            plan_name=plan_name,

            description=description,

            is_public=is_public,

            is_active=True
        )

        return await (
            plan_repository
            .create(
                db,
                plan
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
        
        plan = await (
            plan_repository
            .get_by_id(
                db,
                plan_id
            )
        )

        if not plan:

            raise ValueError(
                "Plan not found"
            )

        plan_version = PlanVersion(

            plan_id=plan_id,

            version_number=
                version_number,

            monthly_token_limit=
                monthly_token_limit,

            monthly_request_limit=
                monthly_request_limit,

            monthly_cost_limit=
                monthly_cost_limit,

            is_active=True
        )

        return await (
            plan_version_repository
            .create(
                db,
                plan_version
            )
        )

    async def create_plan_price(
        self,
        db,
        plan_version_id: int,
        provider: str,
        currency: str,
        amount,
        billing_cycle: str,
        external_price_id: str = None
    ):
        
        version = await (
            plan_version_repository
            .get_by_id(
                db,
                plan_version_id
            )
        )

        if not version:

            raise ValueError(
                "Plan version not found"
            )

        plan_price = PlanPrice(

            plan_version_id=
                plan_version_id,

            provider=
                provider,

            external_price_id=
                external_price_id,

            currency=
                currency,

            amount=
                amount,

            billing_cycle=
                billing_cycle,

            is_active=True
        )

        return await (
            plan_price_repository
            .create(
                db,
                plan_price
            )
        )

    
    async def get_by_plan_code(
        self,
        db,
        plan_code: str
    ):

        return await (
            plan_repository
            .get_by_code(
                db,
                plan_code
            )
        )
    
    async def get_by_id(
        self,
        db,
        plan_id: int
    ):

        return await (
            plan_repository
            .get_by_id(
                db,
                plan_id
            )
        )

    async def get_public_plans(
        self,
        db
    ):

        return await (
            plan_repository
            .get_public_plans(
                db
            )
        )
    
    async def get_all_plans(
        self,
        db
    ):

        return await (
            plan_repository
            .get_all(
                db
            )
        )

    async def get_active_version(
        self,
        db,
        plan_id: int
    ):

        return await (
            plan_version_repository
            .get_active_by_plan(
                db,
                plan_id
            )
        )

    async def get_active_price(
        self,
        db,
        plan_version_id: int,
        provider: str,
        billing_cycle: str,
        currency: str
    ):

        return await (
            plan_price_repository
            .get_active_price(

                db,

                plan_version_id,

                provider,

                billing_cycle,

                currency
            )
        )

    async def get_checkout_plan(
        self,
        db,
        plan_code: str,
        provider: str,
        billing_cycle: str,
        currency: str
    ):

        plan = await (
            plan_repository
            .get_by_code(
                db,
                plan_code
            )
        )

        if not plan:

            raise ValueError(
                "Plan not found"
            )

        version = await (
            plan_version_repository
            .get_active_by_plan(
                db,
                plan.id
            )
        )

        if not version:

            raise ValueError(
                "Active plan version not found"
            )

        price = await (
            plan_price_repository
            .get_active_price(

                db,

                version.id,

                provider,

                billing_cycle,

                currency
            )
        )

        if not price:

            raise ValueError(
                "Plan pricing not found"
            )

        return {

            "plan":
                plan,

            "version":
                version,

            "price":
                price
        }


plan_service = (
    PlanService()
)