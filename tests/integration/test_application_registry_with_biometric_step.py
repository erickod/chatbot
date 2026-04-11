from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.application.services.usecase_registry import UseCaseRegistry
from chatbot.application.usecases.request_biometric_validation_step import (
    RequestBiometricValidationStep,
)
from chatbot.domain.entities.application import ApplicationStatus
from chatbot.domain.entities.biometric_validation import BiometricValidationStatus
from chatbot.infra.orm.sqlalchemy.models import (
    DBApplication,
    DBBiometricValidation,
    DBStepExecution,
)
from chatbot.infra.repositories.sa_load_application_repository import (
    SAApplicationRepository,
)
from chatbot.infra.repositories.save_biometric_validation_repository import (
    SASaveBiometricValidationRepository,
)


async def test_given_application_when_save_biometric_then_biometric_row_persisted(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application stored in the database
    WHEN  SASaveBiometricValidationRepository.run() is called with a BiometricValidation entity
    THEN  a DBBiometricValidation row is persisted with correct field values
    """
    from chatbot.domain.entities.biometric_validation import BiometricValidation

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
    repo = SASaveBiometricValidationRepository(db)
    await repo.run(biometric)
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
    WHEN  SASaveBiometricValidationRepository.run() is called with a BiometricValidation entity
    THEN  a DBStepExecution row is persisted with data containing profile_ref and validation_result
    """
    from chatbot.domain.entities.biometric_validation import BiometricValidation

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
    repo = SASaveBiometricValidationRepository(db)
    await repo.run(biometric)
    await db.flush()

    step = await db.get(DBStepExecution, biometric.step_execution.id)
    assert step is not None
    assert step.data["profile_ref"] == "profile-xyz"
    assert step.data["validation_result"] == {"score": 0.75}
    assert "message" not in step.data


async def test_given_application_when_registry_runs_biometric_step_then_await_confirmation(
    db: AsyncSession,
) -> None:
    """
    GIVEN an application in the database matching the input phones
    WHEN  UseCaseRegistry.run() executes the 'biometric' step
    THEN  the output status is AWAIT_CONFIRMATION and both DB rows are persisted
    """
    db_app = DBApplication(
        originator_phone="orig_bio_3",
        company_phone="appl_bio_3",
        status=ApplicationStatus.IN_PROGRESS,
    )
    db.add(db_app)
    await db.flush()

    registry = UseCaseRegistry()
    registry.register_step(
        RequestBiometricValidationStep(
            save_biometric_repo=SASaveBiometricValidationRepository(db),
            load_application_repo=SAApplicationRepository(db),
        )
    )

    data = dict(
        originator_phone="orig_bio_3",
        company_phone="appl_bio_3",
        profile_ref="profile-reg",
        validation_result={"score": 0.90},
    )
    output = await registry.run(data, name="biometric")

    assert output.id is not None
    assert output.step_execution_id is not None
    assert output.status == BiometricValidationStatus.AWAIT_CONFIRMATION

    biometric_row = await db.get(DBBiometricValidation, output.id)
    assert biometric_row is not None
    assert biometric_row.profile_ref == "profile-reg"

    step_row = await db.get(DBStepExecution, output.step_execution_id)
    assert step_row is not None
    assert step_row.data["profile_ref"] == "profile-reg"
    assert step_row.data["validation_result"] == {"score": 0.90}


async def test_given_no_application_when_biometric_step_runs_then_blocked(
    db: AsyncSession,
) -> None:
    """
    GIVEN no application exists in the database for the given phones
    WHEN  UseCaseRegistry.run() executes the 'biometric' step
    THEN  the output status is BLOCKED, step_execution_id is None, and no rows are persisted
    """
    registry = UseCaseRegistry()
    registry.register_step(
        RequestBiometricValidationStep(
            save_biometric_repo=SASaveBiometricValidationRepository(db),
            load_application_repo=SAApplicationRepository(db),
        )
    )

    data = dict(
        originator_phone="unknown_orig",
        company_phone="unknown_appl",
        profile_ref="profile-ghost",
        validation_result={"score": 0.0},
    )
    output = await registry.run(data, name="biometric")

    assert output.status == BiometricValidationStatus.BLOCKED
    assert output.id is None
    assert output.step_execution_id is None
    assert output.message == "Application not found"

    biometrics = await db.execute(select(DBBiometricValidation))
    assert biometrics.scalars().all() == []

    steps = await db.execute(select(DBStepExecution))
    assert steps.scalars().all() == []
