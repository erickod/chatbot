from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.save_caller_step import SaveNameStep
from chatbot.domain.entities.application import Application, ApplicationStatus
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_caller_repository import FakeCallerRepository


async def test_given_application_exists_when_registry_runs_name_step_then_completed() -> (
    None
):
    """
    GIVEN an application matching the input phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'name' step
    THEN  the output status is COMPLETED and the caller is stored with the given name
    """
    application = Application.create(
        originator_phone="originator_phone",
        company_phone="company_phone",
    )
    fake_caller_repo = FakeCallerRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        SaveNameStep(
            save_caller_repo=fake_caller_repo,
            load_application_repo=FakeApplicationRepository(seed=[application]),
        )
    )

    output = await registry.run(
        dict(
            originator_phone="originator_phone",
            company_phone="company_phone",
            value="John Doe",
        ),
        name="name",
    )

    assert output.id
    assert output.step_execution_id
    assert output.status == ApplicationStatus.COMPLETED
    caller = fake_caller_repo.by_id[output.id]
    assert caller.name == "John Doe"


async def test_given_no_application_when_registry_runs_name_step_then_blocked() -> None:
    """
    GIVEN no application exists for the given phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'name' step
    THEN  the output status is BLOCKED and no caller is stored
    """
    fake_caller_repo = FakeCallerRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        SaveNameStep(
            save_caller_repo=fake_caller_repo,
            load_application_repo=FakeApplicationRepository(),
        )
    )

    output = await registry.run(
        dict(originator_phone="unknown", company_phone="unknown", value="John Doe"),
        name="name",
    )

    assert output.status == ApplicationStatus.BLOCKED
    assert not fake_caller_repo.by_id
