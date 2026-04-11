from uuid import UUID

from sqlalchemy import select

from chatbot.domain.entities.application_document import (
    ApplicationDocument,
    DocumentEligibilityStatus,
)
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBOApplicationDocument


class SALoadApplicationDocumentRepository(BaseRepository):
    async def run(self, application_id: UUID) -> ApplicationDocument | None:
        db_document = (
            await self.db_session.execute(
                select(DBOApplicationDocument).where(
                    DBOApplicationDocument.application_id == application_id
                )
            )
        ).scalar_one_or_none()
        if not db_document:
            return None
        return ApplicationDocument(
            id=db_document.id,
            application_id=db_document.application_id,
            document=db_document.document,
            status=DocumentEligibilityStatus(db_document.status),
            created_at=db_document.created_at,
            updated_at=db_document.updated_at,
        )
