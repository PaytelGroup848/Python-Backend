from app.modules.billing.constants.payment_provider import (
    STRIPE,
    RAZORPAY
)

from app.modules.billing.providers.stripe_provider import (
    StripeProvider
)

from app.modules.billing.providers.razorpay_provider import (
    RazorpayProvider
)

provider_registry = {

    STRIPE:
        StripeProvider(),

    RAZORPAY:
        RazorpayProvider()
}