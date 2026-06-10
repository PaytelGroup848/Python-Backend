from app.modules.billing.providers.stripe_provider import (
    StripeProvider
)

provider_registry = {

    "stripe": StripeProvider(),
}