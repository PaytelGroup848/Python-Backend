from app.modules.billing.services.invoice_service import (
    invoice_service
)

from app.modules.billing.services.company_settings_service import (
    company_settings_service
)

from app.modules.billing.repositories.subscription_repository import (
    subscription_repository
)

from app.modules.billing.repositories.payment_repository import (
    payment_repository
)

from app.modules.auth.repositories.user_repository import (
    user_repository
)


class InvoiceDataService:

    async def build_invoice_data(
        self,
        db,
        invoice_id: int
    ):

        company = await (
            company_settings_service
            .get_company_settings(
                db
            )
        )

        invoice = await (
            invoice_service
            .get_invoice_by_id(
                db,
                invoice_id
            )
        )

        if not invoice:

            return None

        user = await (
            user_repository
            .get_by_id(
                db,
                invoice.user_id
            )
        )

        subscription = None

        if invoice.subscription_id:

            subscription = await (
                subscription_repository
                .get_by_id(
                    db,
                    invoice.subscription_id
                )
            )

        payment = await (
            payment_repository
            .get_by_invoice_id(
                db,
                invoice.id
            )
        )

        return {

            "company": company,

            "invoice": invoice,

            "user": user,

            "subscription": subscription,

            "payment": payment
        }


invoice_data_service = (
    InvoiceDataService()
)