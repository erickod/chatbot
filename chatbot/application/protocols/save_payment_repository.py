from chatbot.domain.entities.payment import Payment


class SavePaymentRepository:
    async def run(self, payment: Payment) -> None: ...
