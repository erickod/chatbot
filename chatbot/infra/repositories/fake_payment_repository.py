from uuid import UUID

from chatbot.domain.entities.payment import Payment


class FakePaymentRepository:
    def __init__(self, seed: list[Payment] = []) -> None:
        self.by_id: dict[UUID, Payment] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[Payment]) -> None:
        for item in seed:
            self.by_id[item.id] = item

    async def create(self, payment: Payment) -> None:
        self._process_seed([payment])
