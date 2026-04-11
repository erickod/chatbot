from uuid import UUID

from chatbot.domain.entities.caller import Caller


class FakeCallerRepository:
    def __init__(self, seed: list[Caller] = []) -> None:
        self.by_id: dict[UUID, Caller] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[Caller]) -> None:
        for item in seed:
            self.by_id[item.id] = item

    async def create(self, caller: Caller) -> None:
        self._process_seed([caller])
