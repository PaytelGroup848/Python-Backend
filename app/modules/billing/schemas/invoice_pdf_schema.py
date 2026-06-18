from pydantic import BaseModel


class InvoicePdfData(BaseModel):

    company: dict

    invoice: dict

    user: dict

    subscription: dict | None

    payment: dict | None