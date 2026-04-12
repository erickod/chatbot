from sqlalchemy import select

from chatbot.domain.entities.application import Application, ApplicationStatus
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBApplication


class SAApplicationRepository(BaseRepository):
    async def get_by_phones(
        self, originator_phone: str, company_phone: str
    ) -> Application | None:
        if not (
            db_app := (
                await self.db_session.execute(
                    select(DBApplication).where(
                        DBApplication.originator_phone == originator_phone,
                        DBApplication.company_phone == company_phone,
                    )
                )
            ).scalar_one_or_none()
        ):
            return None
        return Application(
            id=db_app.id,
            status=ApplicationStatus(db_app.status),
            originator_phone=db_app.originator_phone,
            company_phone=db_app.company_phone,
            created_at=db_app.created_at,
            updated_at=db_app.updated_at or db_app.created_at,
            originator_code=db_app.originator_code,
            completed_at=db_app.completed_at,
        )
