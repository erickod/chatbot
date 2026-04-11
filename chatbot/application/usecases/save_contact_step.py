from uuid import UUID

from pydantic import BaseModel

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.application.protocols.save_contact_repository import ContactRepository
from chatbot.domain.entities.application_contact import (
    ApplicationContact,
    ContactStatus,
)


class ContactStepInput(BaseModel):
    originator_phone: str
    company_phone: str
    cpf: str | None = None
    name: str | None = None
    email: str | None = None
    role: str | None = None


class ContactStepOutput(BaseModel):
    id: UUID | None
    step_execution_id: UUID | None
    status: str
    message: str | None = None


class SaveContactStep:
    input_schema: type[ContactStepInput] = ContactStepInput
    output_schema: type[ContactStepOutput] = ContactStepOutput
    name: str = "contact"

    def __init__(
        self,
        contact_repo: ContactRepository,
        application_repo: ApplicationRepository,
    ) -> None:
        self._contact_repo = contact_repo
        self._application_repo = application_repo

    async def execute(self, input: ContactStepInput) -> ContactStepOutput:
        application = await self._application_repo.get_by_phones(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
        )
        if not application:
            contact = ApplicationContact.create(
                application_id=UUID(int=0),
                cpf=input.cpf,
                name=input.name,
                email=input.email,
                role=input.role,
            )
            contact.block(message="Application not found")
            return ContactStepOutput(
                id=None,
                step_execution_id=None,
                status=ContactStatus.BLOCKED,
                message=contact.message,
            )
        contact = ApplicationContact.create(
            application_id=application.id,
            cpf=input.cpf,
            name=input.name,
            email=input.email,
            role=input.role,
        )
        application.advance_step(contact.step_execution)
        await self._contact_repo.create(contact)
        return ContactStepOutput(
            id=contact.id,
            step_execution_id=contact.step_execution.id,
            status=contact.status,
        )
