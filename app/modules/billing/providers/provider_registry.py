from app.modules.billing.constants.payment_provider import (
    STRIPE
)

from app.modules.billing.providers.stripe_provider import (
    StripeProvider
)

provider_registry = {

    STRIPE: StripeProvider(),
}