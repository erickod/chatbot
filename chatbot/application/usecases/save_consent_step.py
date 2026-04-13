from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.application.protocols.consent_repository import ConsentRepository
from chatbot.domain.entities.consent import Consent


class Input(BaseModel):
    originator_phone: str
    company_phone: str
    status: Literal["DECLINED", "ACCEPTED"]
    term_id: UUID = UUID("019d8300-1de5-704b-8782-42a0ec84287e")


class Output(BaseModel):
    id: UUID | None
    step_name: str
    status: str = "PENDING"


class SaveTermsStep:
    input_schema = Input
    output_schema = Output
    name: str = "summary"

    def __init__(
        self,
        *,
        application_repository: ApplicationRepository,
        consent_repository: ConsentRepository,
    ) -> None:
        self._application_repository = application_repository
        self._consent_repository = consent_repository

    async def execute(self, input: Input) -> Output:
        if application := await self._application_repository.get_by_phones(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
        ):
            consent = Consent.create(
                application_id=application.id, term_id=input.term_id
            )
            consent.accept() if input.status == "ACCEPTED" else consent.decline()
            await self._consent_repository.create(consent)
            return Output(step_name=self.name, status=consent.status, id=consent.id)
        return Output(step_name=self.name, id=None)
