from typing import Protocol

from chatbot.domain.entities.caller import Caller


class CallerRepository(Protocol):
    async def create(self, caller: Caller) -> None: ...
    async def load_by_phones(
        self, originator_phone: str, company_phone: str
    ) -> Caller | None: ...
