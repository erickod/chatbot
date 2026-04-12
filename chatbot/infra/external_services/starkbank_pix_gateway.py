from datetime import timedelta

import starkbank
from sqlalchemy import UUID

from chatbot.domain.entities.payment import Payment
from chatbot.settings import settings


class StarkbankPixGatewayAdapter:
    """
    Usando a lib do startkbank,
    o brcode.uuid -> UUID(brcode.uuid)
    se torna -> UUID('11748720-23f4-4ba9-84ec-ad3f811b1393')
    -> para a tabela pix_id
    """

    async def create_charge(self, payment: Payment) -> None:
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
        for brcode in brcodes:
            payment.register_gateway_reference(
                gateway="starkbank", ref=str(UUID(brcode.UUID))
            )
