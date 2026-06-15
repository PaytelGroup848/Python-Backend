from app.modules.billing.constants.payment_provider import (
    STRIPE,
    RAZORPAY,
    CASHFREE,
    PAYPAL,
    PHONEPE
)

from app.modules.billing.providers.stripe_provider import (
    StripeProvider
)

from app.modules.billing.providers.razorpay_provider import (
    RazorpayProvider
)

from app.modules.billing.providers.cashfree_provider import (
    CashfreeProvider
)

from app.modules.billing.providers.paypal_provider import (
    PayPalProvider
)

from app.modules.billing.providers.phonepe_provider import (
    PhonePeProvider
)


provider_registry = {

    STRIPE:
        StripeProvider(),

    RAZORPAY:
        RazorpayProvider(),

    CASHFREE:
        CashfreeProvider(),

    PAYPAL:
        PayPalProvider(),

    PHONEPE:
        PhonePeProvider()
}