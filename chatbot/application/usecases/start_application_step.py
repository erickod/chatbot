from uuid import UUID

from pydantic import BaseModel

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.domain.entities.application import Application, ApplicationStatus


class Input(BaseModel):
    originator_phone: str
    company_phone: str


class Output(BaseModel):
    id: UUID | None = None
    status: str


class StartApplicationStep:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output

    def __init__(self, *, application_repository: ApplicationRepository) -> None:
        self.application_repository = application_repository

    async def execute(self, input: Input) -> Output:
        application = Application.create(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
            status=ApplicationStatus.PENDING,
        )
        await self.application_repository.create(application)
        return Output(id=application.id, status=application.status)
