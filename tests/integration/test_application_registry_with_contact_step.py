from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.save_contact_step import SaveContactStep
from chatbot.domain.entities.application import Application
from chatbot.domain.entities.application_contact import ContactStatus
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_contact_repository import FakeContactRepository


async def test_given_application_when_registry_runs_contact_step_then_completed() -> (
    None
):
    """
    GIVEN an application matching the input phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'contact' step
    THEN  the output status is COMPLETED and the contact is stored with the given data
    """
    application = Application.create(originator_phone="orig", company_phone="comp")
    fake_contact_repo = FakeContactRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        SaveContactStep(
            save_contact_repo=fake_contact_repo,
            load_application_repo=FakeApplicationRepository(seed=[application]),
        )
    )

    output = await registry.run(
        dict(
            originator_phone="orig",
            company_phone="comp",
            cpf="11122233344",
            name="Alice",
            email="alice@example.com",
            role="owner",
        ),
        name="contact",
    )

    assert output.id is not None
    assert output.step_execution_id is not None
    assert output.status == ContactStatus.COMPLETED
    contact = fake_contact_repo.by_id[output.id]
    assert contact.name == "Alice"
    assert contact.cpf == "11122233344"


async def test_given_no_application_when_contact_step_runs_then_blocked() -> None:
    """
    GIVEN no application exists for the given phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'contact' step
    THEN  the output status is BLOCKED and no contact is stored
    """
    fake_contact_repo = FakeContactRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        SaveContactStep(
            save_contact_repo=fake_contact_repo,
            load_application_repo=FakeApplicationRepository(),
        )
    )

    output = await registry.run(
        dict(
            originator_phone="unknown",
            company_phone="unknown",
            cpf="00000000000",
            name="Ghost",
            email="ghost@example.com",
            role="owner",
        ),
        name="contact",
    )

    assert output.status == ContactStatus.BLOCKED
    assert output.id is None
    assert output.step_execution_id is None
    assert output.message == "Application not found"
    assert not fake_contact_repo.by_id
