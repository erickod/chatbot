from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.application.protocols.save_caller_repository import CallerRepository
from chatbot.domain.entities.caller import Caller, NameStepStatus


class Input(BaseModel):
    originator_phone: str
    company_phone: str
    value: str = Field(validation_alias=AliasChoices("value", "name"))


class Output(BaseModel):
    id: UUID | None = None
    step_execution_id: UUID | None = None
    status: str


class SaveNameStep:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output
    name: str = "name"

    def __init__(
        self,
        caller_repo: CallerRepository,
        application_repo: ApplicationRepository,
    ) -> None:
        self._caller_repo = caller_repo
        self._application_repo = application_repo

    async def execute(self, input: Input) -> Output:
        application = await self._application_repo.get_by_phones(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
        )
        if not application:
            return Output(status=NameStepStatus.BLOCKED)
        caller = Caller.create(name=input.value, application_id=application.id)
        application.advance_step(caller.step_execution)
        await self._caller_repo.create(caller)
        return Output(
            id=caller.id,
            step_execution_id=caller.step_execution.id,
            status=caller.status,
        )
