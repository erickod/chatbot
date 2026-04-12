from uuid import UUID

from chatbot.domain.entities.application import Application


class FakeApplicationRepository:
    def __init__(self, seed: list[Application] = []) -> None:
        self.by_id: dict[UUID, Application] = {}
        self.by_phones: dict[tuple[str, str], Application] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[Application]) -> None:
        for item in seed:
            self.by_id[item.id] = item
            self.by_phones[(item.originator_phone, item.company_phone)] = item

    async def get_by_phones(
        self, originator_phone: str, company_phone: str
    ) -> Application | None:
        return self.by_phones.get((originator_phone, company_phone))

    async def create(self, application: Application) -> None:
        self._process_seed([application])

    async def get_by_id(self, id: UUID) -> Application | None:
        return self.by_id.get(id)
