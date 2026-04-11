from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.save_caller_step import SaveCallerStep
from chatbot.domain.entities.application import ApplicationStatus
from chatbot.domain.entities.caller import Caller
from chatbot.infra.orm.sqlalchemy.models import DBApplication, DBStepExecution
from chatbot.infra.repositories.sa_load_application_repository import (
    SAApplicationRepository,
)
from chatbot.infra.repositories.save_caller_repository import SASaveCallerRepository


async def test_given_application_in_db_when_load_by_phones_then_returns_application(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database with matching phones
    WHEN  load_application_repository.run() is called with those phones
    THEN  it returns the corresponding Application domain entity
    """
    db_app = DBApplication(
        originator_phone="orig_phone",
        company_phone="appl_phone",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    repo = SAApplicationRepository(db)
    result = await repo.get_by_phones(
        originator_phone="orig_phone", company_phone="appl_phone"
    )

    assert result is not None
    assert result.originator_phone == "orig_phone"
    assert result.company_phone == "appl_phone"
    assert result.status == ApplicationStatus.IN_PROGRESS


async def test_given_no_application_in_db_when_load_by_phones_then_returns_none(
    db: AsyncSession,
) -> None:
    """
    GIVEN no application exists in the database for the given phones
    WHEN  load_application_repository.run() is called
    THEN  it returns None
    """
    repo = SAApplicationRepository(db)
    result = await repo.get_by_phones(
        originator_phone="unknown", company_phone="unknown"
    )

    assert result is None


async def test_given_caller_when_save_then_step_execution_persisted_with_name(
    db: AsyncSession,
) -> None:
    """
    GIVEN a Caller domain entity created with a name and an existing application
    WHEN  save_caller_repository.run() is called
    THEN  a DBStepExecution row is persisted with data["name"] equal to caller.name
    """
    db_app = DBApplication(
        originator_phone="orig_phone2",
        company_phone="appl_phone2",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    caller = Caller.create(name="Jane Doe", application_id=db_app.id)
    repo = SASaveCallerRepository(db)
    await repo.run(caller)
    await db.flush()

    result = await db.get(DBStepExecution, caller.step_execution.id)
    assert result is not None
    assert result.data["name"] == "Jane Doe"


async def test_given_application_exists_when_registry_runs_name_step_then_completed(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application in the database matching the input phones
    WHEN  UseCaseRegistry.run() executes the 'name' step
    THEN  the output status is COMPLETED and the step execution is persisted in the DB
    """
    db_app = DBApplication(
        originator_phone="originator_phone",
        company_phone="company_phone",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    registry = UseCaseRegistry()
    registry.register_step(
        SaveCallerStep(
            save_caller_repo=SASaveCallerRepository(db),
            load_application_repo=SAApplicationRepository(db),
        )
    )

    data = dict(
        originator_phone="originator_phone",
        company_phone="company_phone",
        value="John Doe",
    )
    output = await registry.run(data, name="name")

    assert output.id
    assert output.step_execution_id
    assert output.status == ApplicationStatus.COMPLETED

    step = await db.get(DBStepExecution, output.step_execution_id)
    assert step is not None
    assert step.data["name"] == "John Doe"
