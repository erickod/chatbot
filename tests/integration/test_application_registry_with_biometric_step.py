from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.request_biometric_validation_step import (
    RequestBiometricValidationStep,
)
from chatbot.domain.entities.application import Application, ApplicationStatus
from chatbot.domain.entities.biometric_validation import (
    BiometricValidation,
    BiometricValidationStatus,
)
from chatbot.infra.orm.sqlalchemy.models import (
    DBApplication,
    DBBiometricValidation,
    DBStepExecution,
)
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_biometric_validation_repository import (
    FakeBiometricValidationRepository,
)
from chatbot.infra.repositories.sa_load_application_repository import (
    SAApplicationRepository,
)
from chatbot.infra.repositories.save_biometric_validation_repository import (
    SABiometricValidationRepository,
)


async def test_given_application_when_save_biometric_then_biometric_row_persisted(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SABiometricValidationRepository.create() is called with a BiometricValidation entity
    THEN  a DBBiometricValidation row is persisted with correct field values
    """
    db_app = DBApplication(
        originator_phone="orig_bio_1",
        company_phone="appl_bio_1",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    biometric = BiometricValidation.create(
        application_id=db_app.id,
        profile_ref="profile-abc",
        validation_result={"score": 0.98},
    )
    repo = SABiometricValidationRepository(db)
    await repo.create(biometric)
    await db.flush()

    result = await db.get(DBBiometricValidation, biometric.id)
    assert result is not None
    assert result.profile_ref == "profile-abc"
    assert result.validation_result == {"score": 0.98}
    assert result.application_id == db_app.id
    assert result.status == BiometricValidationStatus.AWAIT_CONFIRMATION


async def test_given_application_when_save_biometric_then_step_execution_persisted(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SABiometricValidationRepository.create() is called with a BiometricValidation entity
    THEN  a DBStepExecution row is persisted with data containing profile_ref and validation_result
    """
    db_app = DBApplication(
        originator_phone="orig_bio_2",
        company_phone="appl_bio_2",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    biometric = BiometricValidation.create(
        application_id=db_app.id,
        profile_ref="profile-xyz",
        validation_result={"score": 0.75},
    )
    repo = SABiometricValidationRepository(db)
    await repo.create(biometric)
    await db.flush()

    step = await db.get(DBStepExecution, biometric.step_execution.id)
    assert step is not None
    assert step.data["profile_ref"] == "profile-xyz"
    assert step.data["validation_result"] == {"score": 0.75}
    assert "message" not in step.data


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


async def test_given_no_application_when_biometric_step_runs_then_blocked(
    db: AsyncSession,
) -> None:
    """
    GIVEN no application exists in the database for the given phones
    WHEN  UseCaseRegistry.run() executes the 'biometric' step
    THEN  the output status is BLOCKED, step_execution_id is None, and no rows are persisted
    """
    from sqlalchemy import select

    registry = UseCaseRegistry()
    registry.register_step(
        RequestBiometricValidationStep(
            save_biometric_repo=SABiometricValidationRepository(db),
            load_application_repo=SAApplicationRepository(db),
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

    biometrics = await db.execute(select(DBBiometricValidation))
    assert biometrics.scalars().all() == []

    steps = await db.execute(select(DBStepExecution))
    assert steps.scalars().all() == []
