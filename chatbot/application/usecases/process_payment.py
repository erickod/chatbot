from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, computed_field

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.application.protocols.load_application_document_repository import (
    DocumentRepository,
)
from chatbot.application.protocols.save_payment_repository import PaymentRepository
from chatbot.domain.entities.application_document import DocumentEligibilityStatus
from chatbot.domain.entities.payment import Payment, PaymentStatus


class Input(BaseModel):
    originator_phone: str
    company_phone: str
    pix_amount_cents: int = 2000


class Output(BaseModel):
    id: UUID | None = None
    step_execution_id: UUID | None = None
    status: str
    pix_transaction_id: str | None = None
    pix_clipboard: str | None = None
    pix_qrcode: str | None = None
    pix_amount_cents: int | None = None
    step_name: str
    message: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pix_amount(self) -> str | None:
        if self.pix_amount_cents is None:
            return None
        return "{:.2f}".format(Decimal(self.pix_amount_cents) / 100)


class RequestPaymentStep:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output
    name: str = "payment"

    def __init__(
        self,
        *,
        payment_repo: PaymentRepository,
        application_repo: ApplicationRepository,
        document_repo: DocumentRepository,
        pix_gateway: StarkbankPixGateway,
    ) -> None:
        self._payment_repo = payment_repo
        self._application_repo = application_repo
        self._document_repo = document_repo
        self._pix_gateway = pix_gateway

    async def execute(self, input: Input) -> Output:
        application = await self._application_repo.get_by_phones(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
        )
        if not application:
            return Output(
                status=PaymentStatus.BLOCKED,
                step_name=self.name,
                message="Application not found",
            )
        application_document = await self._document_repo.get_by_application_id(
            application.id
        )
        if (
            not application_document
            or not application_document.document
            or application_document.status != DocumentEligibilityStatus.COMPLETED
        ):
            return Output(
                status=PaymentStatus.BLOCKED,
                step_name=self.name,
                message="Application document not found",
            )
        payment = Payment.create(
            application_id=application.id,
            amount_cents=input.pix_amount_cents,
            qr_code_text=None,
            qr_code_uri=None,
            expires_at=None,
            national_id=application_document.document,
        )
        await self._pix_gateway.create_charge(payment)
        application.advance_step(payment.step_execution)
        await self._payment_repo.create(payment)
        return Output(
            id=payment.id,
            step_execution_id=payment.step_execution.id,
            status=payment.status,
            pix_transaction_id=payment.provider_id,
            pix_clipboard=payment.qr_code_text,
            pix_qrcode=payment.qr_code_uri,
            pix_amount_cents=payment.amount_cents,
            step_name=self.name,
        )
