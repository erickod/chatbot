from typing import Protocol

from chatbot.domain.entities.payment import Payment


class PaymentRepository(Protocol):
    async def create(self, payment: Payment) -> None: ...
