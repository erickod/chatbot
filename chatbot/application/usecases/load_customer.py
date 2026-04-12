from uuid import UUID

from pydantic import BaseModel, ConfigDict

from chatbot.application.protocols.save_company_repository import CompanyRepository


class Input(BaseModel):
    originator_phone: str
    company_phone: str


class Output(BaseModel):
    id: UUID | None = None
    value: str | None = None
    trading_name: str | None = ""
    status: str
    step_name: str
    message: str = ""

    model_config = ConfigDict(json_encoders={UUID: str})


class LoadCustomer:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output
    name: str = "cnpj"

    def __init__(self, *, company_repo: CompanyRepository) -> None:
        self.company_repo = company_repo

    async def execute(self, input: Input) -> Output:
        customer = await self.company_repo.load_by_phones(
            originator_phone=input.originator_phone, company_phone=input.company_phone
        )
        if not customer:
            return Output(
                status="PENDING",
                step_name=self.name,
            )
        return Output(
            id=customer.id,
            status=customer.status,
            step_name=self.name,
            value=customer.national_id.value,
            trading_name=customer.trading_name,
        )
