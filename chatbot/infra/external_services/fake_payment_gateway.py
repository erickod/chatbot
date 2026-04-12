from uuid import uuid7

from chatbot.domain.entities.payment import Payment


class FakePaymentGateway:
    async def create_charge(self, payment: Payment) -> None:
        payment.register_gateway_reference(
            gateway=self.__class__.__name__,
            ref=uuid7().hex,
            transaction_id="transaction_id",
            qr_code_text="qr_code_text",
            qr_code_uri="qr_code_uri",
            expires_at=None,
        )
