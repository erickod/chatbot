from uuid import UUID

from pydantic import BaseModel, ConfigDict

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.domain.entities.application import Application, ApplicationStatus


class Input(BaseModel):
    originator_phone: str
    company_phone: str


class Output(BaseModel):
    id: UUID | None = None
    status: str
    step_name: str

    model_config = ConfigDict(json_encoders={UUID: str})


class StartApplicationStep:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output
    name: str = "application"

    def __init__(self, *, application_repository: ApplicationRepository) -> None:
        self.application_repository = application_repository

    async def execute(self, input: Input) -> Output:
        application = Application.create(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
            status=ApplicationStatus.IN_PROGRESS,
        )
        await self.application_repository.create(application)
        return Output(id=application.id, status=application.status, step_name=self.name)
