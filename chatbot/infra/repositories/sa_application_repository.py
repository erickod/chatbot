from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

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

    async def create(self, application: Application) -> None:
        stmt = (
            insert(DBApplication)
            .values(
                id=application.id,
                registration_id=str(application.registration_id),
                originator_phone=application.originator_phone,
                company_phone=application.company_phone,
                status=application.status,
                originator_code=None,
                completed_at=None,
                created_at=application.created_at,
                updated_at=application.updated_at,
            )
            .on_conflict_do_update(
                index_elements=[
                    DBApplication.originator_phone,
                    DBApplication.company_phone,
                ],
                set_={"updated_at": application.updated_at},
            )
        ).returning(DBApplication)
        if not (row := (await self.db_session.execute(stmt)).scalar_one_or_none()):
            return
        application.id = row.id
        application.created_at = row.created_at
        application.updated_at = row.updated_at or row.created_at
        application.status = row.status
        application.originator_code = row.originator_code
        application.completed_at = row.completed_at
        await self.db_session.commit()

    async def get_by_id(self, id: UUID) -> Application | None:
        raise NotImplementedError
