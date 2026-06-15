from abc import ABC
from abc import abstractmethod


class BasePaymentProvider(
    ABC
):

    @abstractmethod
    async def create_payment(
        self,
        amount,
        currency,
        metadata=None
    ):
        pass

    @abstractmethod
    async def verify_payment(
        self,
        payload
    ):
        pass

    @abstractmethod
    async def verify_webhook(
        self,
        payload,
        signature
    ):
        pass

   