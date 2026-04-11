from datetime import datetime, timezone
from uuid import uuid7

from chatbot.domain.entities.application import Application, ApplicationStatus


class FakeApplicationRepository:
    async def run(
        self, originator_phone: str, company_phone: str
    ) -> Application | None:
        now = datetime.now(tz=timezone.utc)
        return Application(
            id=uuid7(),
            status=ApplicationStatus.IN_PROGRESS,
            originator_phone=originator_phone,
            company_phone=company_phone,
            created_at=now,
            updated_at=now,
        )
