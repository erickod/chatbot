from uuid import UUID

from chatbot.domain.entities.payment import Payment


class FakePaymentRepository:
    def __init__(
        self, seed: list[Payment] = [], direct_return: Payment | None = None
    ) -> None:
        self.by_id: dict[UUID, Payment] = {}
        self.by_provider: dict[tuple[str | None, str | None], Payment] = {}
        self.direct_return = direct_return
        self._process_seed(seed)

    def _process_seed(self, seed: list[Payment]) -> None:
        for item in seed:
            self.by_id[item.id] = item
            self.by_provider[item.provider, item.provider_id] = item

    async def create(self, payment: Payment) -> None:
        self._process_seed([payment])

    async def load_by_provider_id(
        self, provider: str, provider_id: str
    ) -> Payment | None:
        if self.direct_return:
            return self.direct_return
        return self.by_provider.get((provider, provider_id), None)

    async def update(self, payment: Payment) -> None:
        self._process_seed([payment])
