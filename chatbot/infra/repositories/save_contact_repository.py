from chatbot.domain.entities.application_contact import ApplicationContact
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import (
    DBOnboardingApplicationContact,
    DBStepExecution,
)


class SASaveContactRepository(BaseRepository):
    async def run(self, contact: ApplicationContact) -> None:
        step = contact.step_execution
        data = {
            "cpf": contact.cpf,
            "name": contact.name,
            "email": contact.email,
            "role": contact.role,
        }
        if contact.message is not None:
            data["message"] = contact.message
        self.db_session.add(
            DBOnboardingApplicationContact(
                id=contact.id,
                application_id=contact.application_id,
                cpf=contact.cpf,
                name=contact.name,
                email=contact.email,
                role=contact.role,
            )
        )
        self.db_session.add(
            DBStepExecution(
                id=step.id,
                application_id=step.application_id,
                name=step.name,
                status=str(step.status),
                data=data,
            )
        )
