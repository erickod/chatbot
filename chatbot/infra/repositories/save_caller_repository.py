from sqlalchemy.dialects.postgresql import insert

from chatbot.domain.entities.caller import Caller
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBStepExecution


class SACallerRepository(BaseRepository):
    async def create(self, caller: Caller) -> None:
        step = caller.step_execution
        stmt = (
            insert(DBStepExecution)
            .values(
                id=step.id,
                application_id=step.application_id,
                name=step.name,
                status=str(step.status),
                data={"name": caller.name},
                created_at=caller.created_at,
                updated_at=caller.updated_at,
            )
            .on_conflict_do_update(
                index_elements=[DBStepExecution.application_id, DBStepExecution.name],
                set_={
                    "data": dict(
                        data={"name": caller.name},
                    ),
                    "created_at": caller.created_at,
                    "updated_at": caller.updated_at,
                },
            )
        ).returning(DBStepExecution)
        if row := (await self.db_session.execute(stmt)).scalar_one_or_none():
            step.id = row.id
            caller.id = row.id
            caller.name = row.data.get("name", "")
            step.status = row.status
            caller.created_at = row.created_at
            caller.updated_at = row.updated_at
            await self.db_session.commit()
