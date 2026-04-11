from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.save_cnpj_step import SaveCnpjStep
from chatbot.domain.entities.application import ApplicationStatus
from chatbot.domain.entities.customer import Customer, CustomerStatus
from chatbot.infra.orm.sqlalchemy.models import DBApplication, DBStepExecution
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_company_repository import FakeCompanyRepository
from chatbot.infra.repositories.sa_load_application_repository import (
    SAApplicationRepository,
)
from chatbot.infra.repositories.save_company_repository import SACompanyRepository

_VALID_CNPJ = "11222333000181"


async def test_given_application_when_save_company_repo_then_step_execution_persisted(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SACompanyRepository.create() is called with a Customer entity
    THEN  a DBStepExecution row is persisted with name='cnpj'
    """
    db_app = DBApplication(
        originator_phone="orig_1",
        company_phone="appl_1",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    customer = Customer.create(national_id=_VALID_CNPJ, application_id=db_app.id)
    await SACompanyRepository(db).create(customer)
    await db.flush()

    result = await db.get(DBStepExecution, customer.step_execution.id)
    assert result is not None
    assert result.name == "cnpj"


async def test_given_application_when_save_company_repo_then_national_id_in_data(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SACompanyRepository.create() is called with a Customer entity
    THEN  DBStepExecution.data contains the normalized national_id
    """
    db_app = DBApplication(
        originator_phone="orig_2",
        company_phone="appl_2",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    customer = Customer.create(national_id=_VALID_CNPJ, application_id=db_app.id)
    await SACompanyRepository(db).create(customer)
    await db.flush()

    result = await db.get(DBStepExecution, customer.step_execution.id)
    assert result is not None
    assert result.data["national_id"] == "11222333000181"


async def test_given_application_when_registry_runs_cnpj_step_then_completed(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application in the database matching the input phones
    WHEN  UseCaseRegistry.run() executes the 'cnpj' step
    THEN  output status is COMPLETED, national_id is normalized, step_execution_id is set
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
        SaveCnpjStep(
            save_company_repo=SACompanyRepository(db),
            load_application_repo=SAApplicationRepository(db),
        )
    )

    output = await registry.run(
        {
            "originator_phone": "orig_3",
            "company_phone": "appl_3",
            "national_id": _VALID_CNPJ,
        },
        name="cnpj",
    )

    assert output.status == CustomerStatus.COMPLETED
    assert output.national_id == "11222333000181"
    assert output.step_execution_id is not None

    step = await db.get(DBStepExecution, output.step_execution_id)
    assert step is not None
    assert step.data["national_id"] == "11222333000181"


async def test_given_no_application_when_cnpj_step_runs_then_blocked() -> None:
    """
    GIVEN no application exists for the given phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'cnpj' step
    THEN  output status is BLOCKED and id and step_execution_id are None
    """
    fake_company_repo = FakeCompanyRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        SaveCnpjStep(
            save_company_repo=fake_company_repo,
            load_application_repo=FakeApplicationRepository(),
        )
    )

    output = await registry.run(
        {
            "originator_phone": "unknown",
            "company_phone": "unknown",
            "national_id": _VALID_CNPJ,
        },
        name="cnpj",
    )

    assert output.status == CustomerStatus.BLOCKED
    assert output.id is None
    assert output.step_execution_id is None
    assert not fake_company_repo.by_id


async def test_given_value_field_in_payload_when_cnpj_step_runs_then_national_id_set(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application in the database and a payload using 'value' instead of 'national_id'
    WHEN  UseCaseRegistry.run() executes the 'cnpj' step
    THEN  national_id is resolved from the 'value' fallback and output is COMPLETED
    """
    db_app = DBApplication(
        originator_phone="orig_5",
        company_phone="appl_5",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    registry = UseCaseRegistry()
    registry.register_step(
        SaveCnpjStep(
            save_company_repo=SACompanyRepository(db),
            load_application_repo=SAApplicationRepository(db),
        )
    )

    output = await registry.run(
        {"originator_phone": "orig_5", "company_phone": "appl_5", "value": _VALID_CNPJ},
        name="cnpj",
    )

    assert output.status == CustomerStatus.COMPLETED
    assert output.national_id == "11222333000181"
