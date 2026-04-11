from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.application.protocols.starkbank_pix_gateway import PixChargePayload
from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.save_payment_step import SavePaymentStep
from chatbot.domain.entities.application import ApplicationStatus
from chatbot.domain.entities.payment import Payment, PaymentStatus
from chatbot.domain.value_objects import NationalIDType
from chatbot.infra.orm.sqlalchemy.models import (
    DBApplication,
    DBOApplicationDocument,
    DBPixCharge,
    DBStepExecution,
)
from chatbot.infra.repositories.load_application_document_repository import (
    SALoadApplicationDocumentRepository,
)
from chatbot.infra.repositories.sa_load_application_repository import (
    SAApplicationRepository,
)
from chatbot.infra.repositories.save_payment_repository import SASavePaymentRepository


class FakeStarkbankPixGateway:
    async def create_charge(self, payment: Payment) -> PixChargePayload:
        assert payment.national_id == "51.834.881/0001-87"
        return PixChargePayload(
            provider="starkbank",
            provider_id="provider-123",
            transaction_id="txn-123",
            qr_code_text="0002012636PIX",
            qr_code_uri="https://example.com/qr-code.png",
            expires_at=datetime(2030, 1, 1),
        )


async def test_given_application_when_save_payment_then_pix_charge_row_persisted(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SASavePaymentRepository.run() is called with a payment entity
    THEN  a DBPixCharge row is persisted with correct field values
    """
    db_app = DBApplication(
        originator_phone="orig_pay_1",
        company_phone="appl_pay_1",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()
    db.add(
        DBOApplicationDocument(
            application_id=db_app.id,
            document_type=NationalIDType.CNPJ.value.lower(),
            document="51.834.881/0001-87",
            status="COMPLETED",
        )
    )

    payment = Payment.create(
        application_id=db_app.id,
        provider="starkbank",
        provider_id="provider-abc",
        transaction_id="txn-abc",
        amount_cents=2000,
        currency="BRL",
        qr_code_text="000201",
        qr_code_uri="https://example.com/qr-a.png",
        expires_at=datetime(2030, 1, 1),
    )
    repo = SASavePaymentRepository(db)
    await repo.run(payment)
    await db.flush()

    result = await db.get(DBPixCharge, payment.id)
    assert result is not None
    assert result.application_id == db_app.id
    assert result.provider == "starkbank"
    assert result.provider_id == "provider-abc"
    assert result.transaction_id == "txn-abc"
    assert result.amount_cents == 2000
    assert result.currency == "BRL"
    assert result.qr_code_text == "000201"
    assert result.qr_code_uri == "https://example.com/qr-a.png"
    assert result.status == PaymentStatus.AWAIT_CONFIRMATION


async def test_given_application_when_save_payment_then_step_execution_data_filled(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SASavePaymentRepository.run() is called with a payment entity
    THEN  a DBStepExecution row is persisted with pix payment data
    """
    db_app = DBApplication(
        originator_phone="orig_pay_2",
        company_phone="appl_pay_2",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()
    db.add(
        DBOApplicationDocument(
            application_id=db_app.id,
            document_type=NationalIDType.CNPJ.value.lower(),
            document="51.834.881/0001-87",
            status="COMPLETED",
        )
    )

    payment = Payment.create(
        application_id=db_app.id,
        provider="starkbank",
        provider_id="provider-step",
        transaction_id="txn-step",
        amount_cents=3456,
        currency="BRL",
        qr_code_text="000201STEP",
        qr_code_uri="https://example.com/qr-b.png",
        expires_at=datetime(2030, 1, 2),
    )
    repo = SASavePaymentRepository(db)
    await repo.run(payment)
    await db.flush()

    step = await db.get(DBStepExecution, payment.step_execution.id)
    assert step is not None
    assert step.data["provider"] == "starkbank"
    assert step.data["provider_id"] == "provider-step"
    assert step.data["amount_cents"] == 3456
    assert step.data["status"] == PaymentStatus.AWAIT_CONFIRMATION


async def test_given_application_when_registry_runs_payment_step_then_await_confirmation(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application in the database matching the input phones
    WHEN  UseCaseRegistry.run() executes the payment step
    THEN  the output status is AWAIT_CONFIRMATION and both DB rows are persisted
    """
    db_app = DBApplication(
        originator_phone="orig_pay_3",
        company_phone="appl_pay_3",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()
    db.add(
        DBOApplicationDocument(
            application_id=db_app.id,
            document_type=NationalIDType.CNPJ.value.lower(),
            document="51.834.881/0001-87",
            status="COMPLETED",
        )
    )

    registry = UseCaseRegistry()
    registry.register_step(
        SavePaymentStep(
            save_payment_repo=SASavePaymentRepository(db),
            load_application_repo=SAApplicationRepository(db),
            load_application_document_repo=SALoadApplicationDocumentRepository(db),
            pix_gateway=FakeStarkbankPixGateway(),
        )
    )

    output = await registry.run(
        {
            "originator_phone": "orig_pay_3",
            "company_phone": "appl_pay_3",
            "pix_amount_cents": 2345,
        },
        name="payment",
    )

    assert output is not None
    assert output.id is not None
    assert output.step_execution_id is not None
    assert output.status == PaymentStatus.AWAIT_CONFIRMATION
    assert output.pix_transaction_id == "provider-123"
    assert output.pix_clipboard == "0002012636PIX"
    assert output.pix_qrcode == "https://example.com/qr-code.png"
    assert output.pix_amount_cents == 2345
    assert output.pix_amount == "23.45"
    assert output.step_name == "payment"

    payment_row = await db.get(DBPixCharge, output.id)
    assert payment_row is not None
    assert payment_row.provider == "starkbank"
    assert payment_row.provider_id == "provider-123"

    step_row = await db.get(DBStepExecution, output.step_execution_id)
    assert step_row is not None
    assert step_row.data["provider"] == "starkbank"
    assert step_row.data["provider_id"] == "provider-123"
    assert step_row.data["amount_cents"] == 2345


async def test_given_no_application_when_payment_step_runs_then_blocked(
    db: AsyncSession,
) -> None:
    """
    GIVEN no application exists in the database for the given phones
    WHEN  UseCaseRegistry.run() executes the payment step
    THEN  the output status is BLOCKED and no rows are persisted
    """
    registry = UseCaseRegistry()
    registry.register_step(
        SavePaymentStep(
            save_payment_repo=SASavePaymentRepository(db),
            load_application_repo=SAApplicationRepository(db),
            load_application_document_repo=SALoadApplicationDocumentRepository(db),
            pix_gateway=FakeStarkbankPixGateway(),
        )
    )

    output = await registry.run(
        {
            "originator_phone": "unknown_orig",
            "company_phone": "unknown_appl",
            "pix_amount_cents": 2000,
        },
        name="payment",
    )

    assert output is not None
    assert output.status == PaymentStatus.BLOCKED
    assert output.id is None
    assert output.step_execution_id is None
    assert output.message == "Application not found"
    assert output.step_name == "payment"

    payments = await db.execute(select(DBPixCharge))
    assert payments.scalars().all() == []

    steps = await db.execute(select(DBStepExecution))
    assert steps.scalars().all() == []


async def test_given_blocked_document_when_payment_step_runs_then_blocked(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application with a blocked application document
    WHEN  UseCaseRegistry.run() executes the payment step
    THEN  the output status is BLOCKED and no payment rows are persisted
    """
    db_app = DBApplication(
        originator_phone="orig_pay_6",
        company_phone="appl_pay_6",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()
    db.add(
        DBOApplicationDocument(
            application_id=db_app.id,
            document_type=NationalIDType.CNPJ.value.lower(),
            document="51.834.881/0001-87",
            status="BLOCKED",
        )
    )

    registry = UseCaseRegistry()
    registry.register_step(
        SavePaymentStep(
            save_payment_repo=SASavePaymentRepository(db),
            load_application_repo=SAApplicationRepository(db),
            load_application_document_repo=SALoadApplicationDocumentRepository(db),
            pix_gateway=FakeStarkbankPixGateway(),
        )
    )

    output = await registry.run(
        {
            "originator_phone": "orig_pay_6",
            "company_phone": "appl_pay_6",
            "pix_amount_cents": 2000,
        },
        name="payment",
    )

    assert output is not None
    assert output.status == PaymentStatus.BLOCKED
    assert output.message == "Application document not found"

    payments = await db.execute(select(DBPixCharge))
    assert payments.scalars().all() == []

    steps = await db.execute(select(DBStepExecution))
    assert steps.scalars().all() == []


async def test_given_payment_step_input_when_loading_application_then_maps_company_phone(
    db: AsyncSession,
) -> None:
    """
    GIVEN a payment step input with company_phone
    WHEN  the payment step loads the application
    THEN  company_phone is mapped to company_phone for the lookup
    """
    db_app = DBApplication(
        originator_phone="orig_pay_4",
        company_phone="mapped_applicant",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()
    db.add(
        DBOApplicationDocument(
            application_id=db_app.id,
            document_type=NationalIDType.CNPJ.value.lower(),
            document="51.834.881/0001-87",
            status="COMPLETED",
        )
    )

    step = SavePaymentStep(
        save_payment_repo=SASavePaymentRepository(db),
        load_application_repo=SAApplicationRepository(db),
        load_application_document_repo=SALoadApplicationDocumentRepository(db),
        pix_gateway=FakeStarkbankPixGateway(),
    )
    output = await step.execute(
        step.input_schema(
            originator_phone="orig_pay_4",
            company_phone="mapped_applicant",
            pix_amount_cents=1999,
        )
    )

    assert output.status == PaymentStatus.AWAIT_CONFIRMATION
    assert output.pix_amount_cents == 1999


async def test_given_application_without_document_when_payment_step_runs_then_blocked(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application without a linked application document
    WHEN  UseCaseRegistry.run() executes the payment step
    THEN  the output status is BLOCKED and no payment rows are persisted
    """
    db_app = DBApplication(
        originator_phone="orig_pay_5",
        company_phone="appl_pay_5",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    registry = UseCaseRegistry()
    registry.register_step(
        SavePaymentStep(
            save_payment_repo=SASavePaymentRepository(db),
            load_application_repo=SAApplicationRepository(db),
            load_application_document_repo=SALoadApplicationDocumentRepository(db),
            pix_gateway=FakeStarkbankPixGateway(),
        )
    )

    output = await registry.run(
        {
            "originator_phone": "orig_pay_5",
            "company_phone": "appl_pay_5",
            "pix_amount_cents": 2000,
        },
        name="payment",
    )

    assert output is not None
    assert output.status == PaymentStatus.BLOCKED
    assert output.message == "Application document not found"

    payments = await db.execute(select(DBPixCharge))
    assert payments.scalars().all() == []
