from uuid import UUID

from chatbot.domain.entities.application_document import ApplicationDocument


class DocumentRepository:
    async def get_by_application_id(
        self, application_id: UUID
    ) -> ApplicationDocument | None: ...
