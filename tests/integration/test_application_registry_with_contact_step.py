from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.save_contact_step import SaveContactStep
from chatbot.domain.entities.application import ApplicationStatus
from chatbot.domain.entities.application_contact import (
    ApplicationContact,
    ContactStatus,
)
from chatbot.infra.orm.sqlalchemy.models import (
    DBApplication,
    DBOnboardingApplicationContact,
    DBStepExecution,
)
from chatbot.infra.repositories.sa_load_application_repository import (
    SAApplicationRepository,
)
from chatbot.infra.repositories.save_contact_repository import SASaveContactRepository


async def test_given_application_when_save_contact_then_contact_row_persisted(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SASaveContactRepository.run() is called with a contact entity
    THEN  a DBOnboardingApplicationContact row is persisted with correct field values
    """
    db_app = DBApplication(
        originator_phone="orig_1",
        company_phone="appl_1",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    contact = ApplicationContact.create(
        application_id=db_app.id,
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )
    repo = SASaveContactRepository(db)
    await repo.run(contact)
    await db.flush()

    result = await db.get(DBOnboardingApplicationContact, contact.id)
    assert result is not None
    assert result.cpf == "12345678900"
    assert result.name == "Jane Doe"
    assert result.email == "jane@example.com"
    assert result.role == "owner"
    assert result.application_id == db_app.id


async def test_given_application_when_save_contact_then_step_execution_data_filled(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SASaveContactRepository.run() is called with a contact entity
    THEN  a DBStepExecution row is persisted with data containing all contact fields
    """
    db_app = DBApplication(
        originator_phone="orig_2",
        company_phone="appl_2",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    contact = ApplicationContact.create(
        application_id=db_app.id,
        cpf="98765432100",
        name="John Doe",
        email="john@example.com",
        role="partner",
    )
    repo = SASaveContactRepository(db)
    await repo.run(contact)
    await db.flush()

    step = await db.get(DBStepExecution, contact.step_execution.id)
    assert step is not None
    assert step.data["cpf"] == "98765432100"
    assert step.data["name"] == "John Doe"
    assert step.data["email"] == "john@example.com"
    assert step.data["role"] == "partner"
    assert "message" not in step.data


async def test_given_application_when_registry_runs_contact_step_then_completed(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application in the database matching the input phones
    WHEN  UseCaseRegistry.run() executes the 'contact' step
    THEN  the output status is COMPLETED and both DB rows are persisted
    """
    db_app = DBApplication(
        originator_phone="orig_3",
        company_phone="appl_3",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    registry = UseCaseRegistry()
    registry.register_step(
        SaveContactStep(
            save_contact_repo=SASaveContactRepository(db),
            load_application_repo=SAApplicationRepository(db),
        )
    )

    data = dict(
        originator_phone="orig_3",
        company_phone="appl_3",
        cpf="11122233344",
        name="Alice",
        email="alice@example.com",
        role="owner",
    )
    output = await registry.run(data, name="contact")

    assert output.id is not None
    assert output.step_execution_id is not None
    assert output.status == ContactStatus.COMPLETED

    contact_row = await db.get(DBOnboardingApplicationContact, output.id)
    assert contact_row is not None
    assert contact_row.name == "Alice"

    step_row = await db.get(DBStepExecution, output.step_execution_id)
    assert step_row is not None
    assert step_row.data["name"] == "Alice"
    assert step_row.data["cpf"] == "11122233344"


async def test_given_no_application_when_contact_step_runs_then_blocked(
    db: AsyncSession,
) -> None:
    """
    GIVEN no application exists in the database for the given phones
    WHEN  UseCaseRegistry.run() executes the 'contact' step
    THEN  the output status is BLOCKED, step_execution_id is None, and no rows are persisted
    """
    registry = UseCaseRegistry()
    registry.register_step(
        SaveContactStep(
            save_contact_repo=SASaveContactRepository(db),
            load_application_repo=SAApplicationRepository(db),
        )
    )

    data = dict(
        originator_phone="unknown_orig",
        company_phone="unknown_appl",
        cpf="00000000000",
        name="Ghost",
        email="ghost@example.com",
        role="owner",
    )
    output = await registry.run(data, name="contact")

    assert output.status == ContactStatus.BLOCKED
    assert output.id is None
    assert output.step_execution_id is None
    assert output.message == "Application not found"

    contacts = await db.execute(select(DBOnboardingApplicationContact))
    assert contacts.scalars().all() == []

    steps = await db.execute(select(DBStepExecution))
    assert steps.scalars().all() == []
