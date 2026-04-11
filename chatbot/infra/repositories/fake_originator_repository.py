from uuid import UUID

from chatbot.domain.entities.originator import Originator


class FakeOriginatorRepository:
    def __init__(self, seed: list[Originator] = []) -> None:
        self.by_id: dict[UUID, Originator] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[Originator]) -> None:
        for item in seed:
            self.by_id[item.id] = item

    async def create(self, originator: Originator) -> None:
        self._process_seed([originator])
