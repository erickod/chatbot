from datetime import timedelta

from chatbot.application.protocols.starkbank_pix_gateway import (
    PixChargePayload,
    StarkbankPixGateway,
)
from chatbot.domain.entities.payment import Payment
from chatbot.settings import settings


class StarkbankPixGatewayAdapter(StarkbankPixGateway):
    """
    Usando a lib do startkbank,
    o brcode.uuid -> UUID(brcode.uuid)
    se torna -> UUID('11748720-23f4-4ba9-84ec-ad3f811b1393')
    -> para a tabela pix_id
    """

    async def create_charge(self, payment: Payment) -> PixChargePayload:
        try:
            import starkbank
        except ImportError as exc:
            raise RuntimeError("starkbank dependency is not installed") from exc
        if not payment.national_id:
            raise ValueError("Payment requires national_id to create StarkBank charge")

        starkbank.user = starkbank.Project(
            environment=settings.STARKBANK_ENVIRONMENT,
            id=settings.STARKBANK_PROJECT_ID,
            private_key=settings.STARKBANK_PRIVATE_KEY,
        )
        brcodes = starkbank.dynamicbrcode.create(
            [
                starkbank.DynamicBrcode(
                    amount=payment.amount_cents,
                    expiration=timedelta(days=7).total_seconds(),
                    tags=[f"payment/{payment.id}"],
                    display_description="payment",
                    rules=[
                        starkbank.dynamicbrcode.Rule(
                            key="allowedTaxIds",
                            value=[payment.national_id],
                        )
                    ],
                )
            ],
            user=starkbank.user,
        )
        brcode = brcodes[0]
        expires_at = None
        if brcode.created and brcode.expiration:
            expires_at = brcode.created + brcode.expiration
        return PixChargePayload(
            provider="starkbank",
            provider_id=brcode.id,
            transaction_id=brcode.uuid,
            qr_code_text=None,
            qr_code_uri=brcode.picture_url,
            expires_at=expires_at,
        )
