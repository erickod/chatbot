from typing import Protocol

from chatbot.domain.entities.application import Application


class ApplicationRepository(Protocol):
    async def get_by_phones(
        self, originator_phone: str, company_phone: str
    ) -> Application | None: ...

    async def create(self, application: Application) -> None: ...
