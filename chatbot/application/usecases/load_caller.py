from uuid import UUID

from pydantic import BaseModel, ConfigDict

from chatbot.application.protocols.save_caller_repository import CallerRepository


class Input(BaseModel):
    originator_phone: str
    company_phone: str


class Output(BaseModel):
    id: UUID | None = None
    value: str | None = None
    status: str
    step_name: str
    message: str = ""

    model_config = ConfigDict(json_encoders={UUID: str})


class LoadCaller:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output
    name: str = "name"

    def __init__(self, *, caller_repo: CallerRepository) -> None:
        self.caller_repo = caller_repo

    async def execute(self, input: Input) -> Output:
        caller = await self.caller_repo.load_by_phones(
            originator_phone=input.originator_phone, company_phone=input.company_phone
        )
        if not caller:
            return Output(
                status="PENDING",
                step_name=self.name,
            )
        return Output(
            id=caller.id, status=caller.status, step_name=self.name, value=caller.name
        )
