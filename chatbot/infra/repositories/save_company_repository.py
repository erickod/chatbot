from chatbot.domain.entities.customer import Customer
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBStepExecution


class SACompanyRepository(BaseRepository):
    async def create(self, customer: Customer) -> None:
        step = customer.step_execution
        self.db_session.add(
            DBStepExecution(
                id=step.id,
                application_id=step.application_id,
                name=step.name,
                status=str(step.status),
                data=step.data,
            )
        )
