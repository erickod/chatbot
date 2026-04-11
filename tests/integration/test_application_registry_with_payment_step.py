from datetime import datetime

from chatbot.application.protocols.starkbank_pix_gateway import PixChargePayload
from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.request_payment_step import RequestPaymentStep
from chatbot.domain.entities.application import Application
from chatbot.domain.entities.application_document import (
    ApplicationDocument,
)
from chatbot.domain.entities.payment import Payment, PaymentStatus
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_document_repository import FakeDocumentRepository
from chatbot.infra.repositories.fake_payment_repository import FakePaymentRepository


class FakeStarkbankPixGateway:
    async def create_charge(self, payment: Payment) -> PixChargePayload:
        return PixChargePayload(
            provider="starkbank",
            provider_id="provider-123",
            transaction_id="txn-123",
            qr_code_text="0002012636PIX",
            qr_code_uri="https://example.com/qr-code.png",
            expires_at=datetime(2030, 1, 1),
        )


def _make_step(
    fake_payment_repo: FakePaymentRepository,
    fake_app_repo: FakeApplicationRepository,
    fake_doc_repo: FakeDocumentRepository,
) -> RequestPaymentStep:
    return RequestPaymentStep(
        payment_repo=fake_payment_repo,
        application_repo=fake_app_repo,
        document_repo=fake_doc_repo,
        pix_gateway=FakeStarkbankPixGateway(),
    )


async def test_given_application_and_document_when_payment_step_runs_then_await_confirmation() -> (
    None
):
    """
    GIVEN an application and a completed document in the fake repositories
    WHEN  UseCaseRegistry.run() executes the 'payment' step
    THEN  the output status is AWAIT_CONFIRMATION and payment is stored in the fake repo
    """
    application = Application.create(originator_phone="orig", company_phone="comp")
    document = ApplicationDocument.create(
        application_id=application.id, document="51.834.881/0001-87"
    )
    fake_payment_repo = FakePaymentRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        _make_step(
            fake_payment_repo,
            FakeApplicationRepository(seed=[application]),
            FakeDocumentRepository(seed=[document]),
        )
    )

    output = await registry.run(
        {"originator_phone": "orig", "company_phone": "comp", "pix_amount_cents": 2345},
        name="payment",
    )

    assert output.id is not None
    assert output.step_execution_id is not None
    assert output.status == PaymentStatus.AWAIT_CONFIRMATION
    assert output.pix_transaction_id == "provider-123"
    assert output.pix_clipboard == "0002012636PIX"
    assert output.pix_qrcode == "https://example.com/qr-code.png"
    assert output.pix_amount_cents == 2345
    assert output.pix_amount == "23.45"
    assert output.step_name == "payment"
    assert output.id in fake_payment_repo.by_id


async def test_given_no_application_when_payment_step_runs_then_blocked() -> None:
    """
    GIVEN no application exists for the given phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'payment' step
    THEN  the output status is BLOCKED with message 'Application not found'
    """
    fake_payment_repo = FakePaymentRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        _make_step(
            fake_payment_repo,
            FakeApplicationRepository(),
            FakeDocumentRepository(),
        )
    )

    output = await registry.run(
        {
            "originator_phone": "unknown",
            "company_phone": "unknown",
            "pix_amount_cents": 2000,
        },
        name="payment",
    )

    assert output.status == PaymentStatus.BLOCKED
    assert output.id is None
    assert output.step_execution_id is None
    assert output.message == "Application not found"
    assert not fake_payment_repo.by_id


async def test_given_blocked_document_when_payment_step_runs_then_blocked() -> None:
    """
    GIVEN an application with a document in BLOCKED status
    WHEN  UseCaseRegistry.run() executes the 'payment' step
    THEN  the output status is BLOCKED with message 'Application document not found'
    """
    application = Application.create(originator_phone="orig", company_phone="comp")
    document = ApplicationDocument.create(
        application_id=application.id, document="51.834.881/0001-87"
    )
    document.block()
    fake_payment_repo = FakePaymentRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        _make_step(
            fake_payment_repo,
            FakeApplicationRepository(seed=[application]),
            FakeDocumentRepository(seed=[document]),
        )
    )

    output = await registry.run(
        {"originator_phone": "orig", "company_phone": "comp", "pix_amount_cents": 2000},
        name="payment",
    )

    assert output.status == PaymentStatus.BLOCKED
    assert output.message == "Application document not found"
    assert not fake_payment_repo.by_id


async def test_given_application_without_document_when_payment_step_runs_then_blocked() -> (
    None
):
    """
    GIVEN an application with no linked document in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'payment' step
    THEN  the output status is BLOCKED with message 'Application document not found'
    """
    application = Application.create(originator_phone="orig", company_phone="comp")
    fake_payment_repo = FakePaymentRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        _make_step(
            fake_payment_repo,
            FakeApplicationRepository(seed=[application]),
            FakeDocumentRepository(),
        )
    )

    output = await registry.run(
        {"originator_phone": "orig", "company_phone": "comp", "pix_amount_cents": 2000},
        name="payment",
    )

    assert output.status == PaymentStatus.BLOCKED
    assert output.message == "Application document not found"
    assert not fake_payment_repo.by_id


async def test_given_company_phone_input_when_payment_step_runs_then_maps_correctly() -> (
    None
):
    """
    GIVEN a payment step input with a specific company_phone value
    WHEN  RequestPaymentStep.execute() is called directly
    THEN  the application is found and payment is created with the correct amount
    """
    application = Application.create(
        originator_phone="orig", company_phone="mapped_applicant"
    )
    document = ApplicationDocument.create(
        application_id=application.id, document="51.834.881/0001-87"
    )
    fake_payment_repo = FakePaymentRepository()
    step = _make_step(
        fake_payment_repo,
        FakeApplicationRepository(seed=[application]),
        FakeDocumentRepository(seed=[document]),
    )

    output = await step.execute(
        step.input_schema(
            originator_phone="orig",
            company_phone="mapped_applicant",
            pix_amount_cents=1999,
        )
    )

    assert output.status == PaymentStatus.AWAIT_CONFIRMATION
    assert output.pix_amount_cents == 1999
