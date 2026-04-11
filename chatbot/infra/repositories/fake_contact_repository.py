from uuid import UUID

from chatbot.domain.entities.application_contact import ApplicationContact


class FakeContactRepository:
    def __init__(self, seed: list[ApplicationContact] = []) -> None:
        self.by_id: dict[UUID, ApplicationContact] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[ApplicationContact]) -> None:
        for item in seed:
            self.by_id[item.id] = item

    async def create(self, contact: ApplicationContact) -> None:
        self._process_seed([contact])
