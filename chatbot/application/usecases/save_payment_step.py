from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, computed_field

from chatbot.application.protocols.load_application_document_repository import (
    LoadApplicationDocumentRepository,
)
from chatbot.application.protocols.save_payment_repository import SavePaymentRepository
from chatbot.application.protocols.starkbank_pix_gateway import StarkbankPixGateway
from chatbot.domain.entities.application_document import DocumentEligibilityStatus
from chatbot.domain.entities.payment import Payment, PaymentStatus


class PaymentStepInput(BaseModel):
    originator_phone: str
    company_phone: str
    pix_amount_cents: int = 2000
    registration_id: UUID | None = None


class PaymentStepOutput(BaseModel):
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


class SavePaymentStep:
    input_schema: type[PaymentStepInput] = PaymentStepInput
    output_schema: type[PaymentStepOutput] = PaymentStepOutput
    name: str = "payment"

    def __init__(
        self,
        *,
        save_payment_repo: SavePaymentRepository,
        load_application_repo: ApplicationRepository,
        load_application_document_repo: LoadApplicationDocumentRepository,
        pix_gateway: StarkbankPixGateway,
    ) -> None:
        self._save_payment_repo = save_payment_repo
        self._load_application_repo = load_application_repo
        self._load_application_document_repo = load_application_document_repo
        self._pix_gateway = pix_gateway

    async def execute(self, input: PaymentStepInput) -> PaymentStepOutput:
        application = await self._load_application_repo.get_by_phones(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
        )
        if not application:
            return PaymentStepOutput(
                status=PaymentStatus.BLOCKED,
                step_name=self.name,
                message="Application not found",
            )
        application_document = await self._load_application_document_repo.run(
            application.id
        )
        if (
            not application_document
            or not application_document.document
            or application_document.status != DocumentEligibilityStatus.COMPLETED
        ):
            return PaymentStepOutput(
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
        charge = await self._pix_gateway.create_charge(payment)
        payment.register_gateway_reference(
            gateway=charge.provider,
            ref=charge.provider_id,
            transaction_id=charge.transaction_id,
            qr_code_text=charge.qr_code_text,
            qr_code_uri=charge.qr_code_uri,
            expires_at=charge.expires_at,
        )
        application.advance_step(payment.step_execution)
        await self._save_payment_repo.run(payment)

        return PaymentStepOutput(
            id=payment.id,
            step_execution_id=payment.step_execution.id,
            status=payment.status,
            pix_transaction_id=payment.provider_id,
            pix_clipboard=payment.qr_code_text,
            pix_qrcode=payment.qr_code_uri,
            pix_amount_cents=payment.amount_cents,
            step_name=self.name,
        )
