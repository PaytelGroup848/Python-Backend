from pydantic import (
    BaseModel
)


class PricingCreate(
    BaseModel
):

    model_name: str

    provider: str

    input_cost_per_1k: float

    output_cost_per_1k: float


class PricingResponse(
    BaseModel
):

    id: int

    model_name: str

    provider: str

    input_cost_per_1k: float

    output_cost_per_1k: float

    is_active: bool

    class Config:

        from_attributes = True