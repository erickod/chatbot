from uuid import UUID

from pydantic import BaseModel

from chatbot.application.protocols.save_payment_repository import PaymentRepository


class Input(BaseModel):
    reference: str
    gateway: str = "Starkbank"


class Output(BaseModel):
    id: UUID | None = None
    status: str
    message: str | None = None


class ConfirmPayment:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output
    name: str = "payment"

    def __init__(self, *, payment_repo: PaymentRepository) -> None:
        self._payment_repo = payment_repo

    async def execute(self, input: Input) -> Output:
        if payment := await self._payment_repo.load_by_provider_id(
            provider=input.gateway, provider_id=input.reference
        ):
            payment.approve()
            await self._payment_repo.update(payment)
            return Output(id=payment.id, status=payment.status)
        return Output(status="ERROR", message="payment not found")
