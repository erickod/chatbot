from uuid import UUID

from chatbot.domain.entities.customer import Customer


class FakeCompanyRepository:
    def __init__(self, seed: list[Customer] = []) -> None:
        self.by_id: dict[UUID, Customer] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[Customer]) -> None:
        for item in seed:
            self.by_id[item.id] = item

    async def create(self, customer: Customer) -> None:
        self._process_seed([customer])
