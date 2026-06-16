from decimal import Decimal

from pydantic import (
    BaseModel,
    Field
)


class CreatePlanRequest(
    BaseModel
):

    plan_code: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    plan_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    description: str | None = None

    is_public: bool = True


class CreatePlanVersionRequest(
    BaseModel
):

    version_number: int = Field(
        ...,
        gt=0
    )

    monthly_token_limit: int = Field(
        ...,
        ge=0
    )

    monthly_request_limit: int = Field(
        ...,
        ge=0
    )

    monthly_cost_limit: int | None = Field(
        default=None,
        ge=0
    )


class CreatePlanPriceRequest(
    BaseModel
):

    provider: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    currency: str = Field(
        ...,
        min_length=3,
        max_length=10
    )

    amount: Decimal = Field(
        ...,
        ge=0
    )

    billing_cycle: str = Field(
        ...,
        min_length=3,
        max_length=20
    )

    external_price_id: str | None = None


class PlanResponse(
    BaseModel
):

    id: int

    plan_code: str

    plan_name: str

    description: str | None

    is_public: bool

    is_active: bool

    class Config:

        from_attributes = True


class PlanVersionResponse(
    BaseModel
):

    id: int

    plan_id: int

    version_number: int

    monthly_token_limit: int

    monthly_request_limit: int

    monthly_cost_limit: int | None

    is_active: bool

    class Config:

        from_attributes = True


class PlanPriceResponse(
    BaseModel
):

    id: int

    plan_version_id: int

    provider: str

    external_price_id: str | None

    currency: str

    amount: Decimal

    billing_cycle: str

    is_active: bool

    class Config:

        from_attributes = True

class UpdatePlanVersionRequest(
    BaseModel
):

    monthly_token_limit: int = Field(
        ...,
        ge=0
    )

    monthly_request_limit: int = Field(
        ...,
        ge=0
    )

    monthly_cost_limit: int | None = Field(
        default=None,
        ge=0
    )

class UpdatePlanPriceRequest(
    BaseModel
):

    provider: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    currency: str = Field(
        ...,
        min_length=3,
        max_length=10
    )

    amount: Decimal = Field(
        ...,
        ge=0
    )

    billing_cycle: str = Field(
        ...,
        min_length=3,
        max_length=20
    )

    external_price_id: str | None = None