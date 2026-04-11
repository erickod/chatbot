from typing import Protocol

from chatbot.domain.entities.payment import Payment


class PaymentRepository(Protocol):
    async def create(self, payment: Payment) -> None: ...
    async def load_by_provider_id(
        self, provider: str, provider_id: str
    ) -> Payment | None: ...
