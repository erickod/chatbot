from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.save_cnpj_step import SaveCnpjStep
from chatbot.domain.entities.application import Application
from chatbot.domain.entities.customer import CustomerStatus
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_company_repository import FakeCompanyRepository

_VALID_CNPJ = "11222333000181"


async def test_given_application_when_registry_runs_cnpj_step_then_completed() -> None:
    """
    GIVEN an application matching the input phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'cnpj' step
    THEN  output status is COMPLETED, national_id is normalized, step_execution_id is set
    """
    application = Application.create(originator_phone="orig_3", company_phone="appl_3")
    fake_company_repo = FakeCompanyRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        SaveCnpjStep(
            save_company_repo=fake_company_repo,
            load_application_repo=FakeApplicationRepository(seed=[application]),
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
    assert fake_company_repo.by_id[output.id].national_id.value == "11222333000181"


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


async def test_given_value_field_in_payload_when_cnpj_step_runs_then_national_id_set() -> (
    None
):
    """
    GIVEN an application in the fake repository and a payload using 'value' instead of 'national_id'
    WHEN  UseCaseRegistry.run() executes the 'cnpj' step
    THEN  national_id is resolved from the 'value' fallback and output is COMPLETED
    """
    application = Application.create(originator_phone="orig_5", company_phone="appl_5")
    fake_company_repo = FakeCompanyRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        SaveCnpjStep(
            save_company_repo=fake_company_repo,
            load_application_repo=FakeApplicationRepository(seed=[application]),
        )
    )

    output = await registry.run(
        {"originator_phone": "orig_5", "company_phone": "appl_5", "value": _VALID_CNPJ},
        name="cnpj",
    )

    assert output.status == CustomerStatus.COMPLETED
    assert output.national_id == "11222333000181"
