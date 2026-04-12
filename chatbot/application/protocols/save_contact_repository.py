from typing import Protocol
from uuid import UUID

from chatbot.domain.entities.application_contact import ApplicationContact


class ContactRepository(Protocol):
    async def create(self, contact: ApplicationContact) -> None: ...
    async def load_by_application_id(self, id: UUID) -> ApplicationContact | None: ...
