from chatbot.domain.entities.caller import Caller
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBStepExecution


class SACallerRepository(BaseRepository):
    async def create(self, caller: Caller) -> None:
        step = caller.step_execution
        self.db_session.add(
            DBStepExecution(
                id=step.id,
                application_id=step.application_id,
                name=step.name,
                status=str(step.status),
                data={"name": caller.name},
            )
        )
