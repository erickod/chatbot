from uuid import UUID

from chatbot.domain.entities.application_document import ApplicationDocument


class LoadApplicationDocumentRepository:
    async def run(self, application_id: UUID) -> ApplicationDocument | None: ...
