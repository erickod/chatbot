from uuid import UUID

from chatbot.domain.entities.consent import Consent


class FakeConsentRepository:
    def __init__(self, seed: list[Consent] = []) -> None:
        self.by_id: dict[UUID, Consent] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[Consent]) -> None:
        for item in seed:
            self.by_id[item.id] = item

    async def create(self, consent: Consent) -> None:
        self._process_seed([consent])
