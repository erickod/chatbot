from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.application.protocols.save_company_repository import CompanyRepository
from chatbot.domain.entities.customer import Customer, CustomerStatus


class Input(BaseModel):
    originator_phone: str
    company_phone: str
    national_id: str = Field(validation_alias=AliasChoices("national_id", "value"))


class Output(BaseModel):
    id: UUID | None = None
    step_execution_id: UUID | None = None
    status: CustomerStatus
    national_id: str | None = None
    step_name: str


class SaveCnpjStep:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output
    name: str = "cnpj"

    def __init__(
        self,
        *,
        company_repo: CompanyRepository,
        application_repo: ApplicationRepository,
    ) -> None:
        self._company_repo = company_repo
        self._application_repo = application_repo

    async def execute(self, input: Input) -> Output:
        application = await self._application_repo.get_by_phones(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
        )
        if not application:
            return Output(
                status=CustomerStatus.BLOCKED,
                step_name=self.name,
            )
        customer = Customer.create(
            national_id=input.national_id,
            application_id=application.id,
        )
        application.advance_step(customer.step_execution)
        await self._company_repo.create(customer)
        return Output(
            id=customer.id,
            step_execution_id=customer.step_execution.id,
            status=customer.status,
            national_id=customer.national_id.value,
            step_name=self.name,
        )
