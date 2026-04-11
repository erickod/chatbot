from chatbot.domain.entities.payment import Payment


class PaymentRepository:
    async def create(self, payment: Payment) -> None: ...
