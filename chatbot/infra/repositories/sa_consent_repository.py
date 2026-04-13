from sqlalchemy.dialects.postgresql import insert

from chatbot.domain.entities import Consent
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBConsent, DBStepExecution


class SAConsentRepository(BaseRepository):
    async def create(self, consent: Consent) -> None:
        consent_stmt = insert(DBConsent).values(
            application_id=consent.application_id,
            term_id=consent.term_id,
            status=consent.choice,
            created_at=consent.created_at,
            updated_at=consent.updated_at,
        )
        await self.db_session.execute(consent_stmt)
        step_stmt = insert(DBStepExecution).values(
            application_id=consent.application_id,
            name=consent.step_execution.name,
            status=consent.status,
            data=consent.model_dump(mode="json"),
            created_at=consent.created_at,
            updated_at=consent.updated_at,
        )
        await self.db_session.execute(step_stmt)
        await self.db_session.commit()
