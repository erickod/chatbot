from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from chatbot.domain.entities.payment import Payment


@dataclass(frozen=True)
class PixChargePayload:
    provider: str
    provider_id: str
    transaction_id: str | None
    qr_code_text: str | None
    qr_code_uri: str | None
    expires_at: datetime | None


class PaymentGateway(Protocol):
    async def create_charge(self, payment: Payment) -> None: ...
