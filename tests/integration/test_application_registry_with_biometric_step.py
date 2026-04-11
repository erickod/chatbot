from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.request_biometric_validation_step import (
    RequestBiometricValidationStep,
)
from chatbot.domain.entities.application import Application
from chatbot.domain.entities.biometric_validation import BiometricValidationStatus
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_biometric_validation_repository import (
    FakeBiometricValidationRepository,
)


async def test_given_application_when_registry_runs_biometric_step_then_await_confirmation() -> (
    None
):
    """
    GIVEN an application matching the input phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'biometric' step
    THEN  the output status is AWAIT_CONFIRMATION and biometric is stored in the fake repo
    """
    application = Application.create(
        originator_phone="orig_bio_3", company_phone="appl_bio_3"
    )
    fake_biometric_repo = FakeBiometricValidationRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        RequestBiometricValidationStep(
            save_biometric_repo=fake_biometric_repo,
            load_application_repo=FakeApplicationRepository(seed=[application]),
        )
    )

    output = await registry.run(
        dict(
            originator_phone="orig_bio_3",
            company_phone="appl_bio_3",
            profile_ref="profile-reg",
            validation_result={"score": 0.90},
        ),
        name="biometric",
    )

    assert output.id is not None
    assert output.step_execution_id is not None
    assert output.status == BiometricValidationStatus.AWAIT_CONFIRMATION
    biometric = fake_biometric_repo.by_id[output.id]
    assert biometric.profile_ref == "profile-reg"
    assert biometric.validation_result == {"score": 0.90}


async def test_given_no_application_when_biometric_step_runs_then_blocked() -> None:
    """
    GIVEN no application exists for the given phones in the fake repository
    WHEN  UseCaseRegistry.run() executes the 'biometric' step
    THEN  the output status is BLOCKED and no biometric is stored
    """
    fake_biometric_repo = FakeBiometricValidationRepository()
    registry = UseCaseRegistry()
    registry.register_step(
        RequestBiometricValidationStep(
            save_biometric_repo=fake_biometric_repo,
            load_application_repo=FakeApplicationRepository(),
        )
    )

    output = await registry.run(
        dict(
            originator_phone="unknown_orig",
            company_phone="unknown_appl",
            profile_ref="profile-ghost",
            validation_result={"score": 0.0},
        ),
        name="biometric",
    )

    assert output.status == BiometricValidationStatus.BLOCKED
    assert output.id is None
    assert output.step_execution_id is None
    assert output.message == "Application not found"
    assert not fake_biometric_repo.by_id
