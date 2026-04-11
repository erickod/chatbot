from uuid import UUID


from chatbot.domain.entities import BiometricValidation, BiometricValidationStatus


def test_given_valid_args_when_create_then_status_is_await_confirmation() -> None:
    """
    GIVEN valid biometric validation arguments
    WHEN  BiometricValidation.create() is called
    THEN  the returned instance has status AWAIT_CONFIRMATION
    """
    biometric = BiometricValidation.create(
        application_id=UUID(int=1),
        provider_id="profile-123",
        provider="idwall",
    )

    assert biometric.status == BiometricValidationStatus.AWAIT_CONFIRMATION


def test_given_valid_args_when_create_then_id_is_generated() -> None:
    """
    GIVEN valid biometric validation arguments
    WHEN  BiometricValidation.create() is called
    THEN  the returned instance has a non-None UUID id
    """
    biometric = BiometricValidation.create(
        application_id=UUID(int=1),
        provider_id="profile-123",
        provider="idwall",
    )

    assert isinstance(biometric.id, UUID)


def test_given_valid_args_when_create_then_step_execution_is_attached() -> None:
    """
    GIVEN valid biometric validation arguments
    WHEN  BiometricValidation.create() is called
    THEN  step_execution is set with matching id and application_id
    """
    biometric = BiometricValidation.create(
        application_id=UUID(int=1),
        provider_id="profile-123",
        provider="idwall",
    )

    assert biometric.step_execution is not None
    assert biometric.step_execution.id == biometric.id
    assert biometric.step_execution.application_id == biometric.application_id


def test_given_valid_args_when_create_then_step_execution_has_biometric_name() -> None:
    """
    GIVEN valid biometric validation arguments
    WHEN  BiometricValidation.create() is called
    THEN  step_execution has name biometric and is not final
    """
    biometric = BiometricValidation.create(
        application_id=UUID(int=1),
        provider_id="profile-123",
        provider="idwall",
    )

    assert biometric.step_execution is not None
    assert biometric.step_execution.name == "biometric"
    assert (
        biometric.step_execution.status == BiometricValidationStatus.AWAIT_CONFIRMATION
    )
    assert biometric.step_execution.is_final is False


def test_given_biometric_when_confirm_called_then_status_is_pending() -> None:
    """
    GIVEN a BiometricValidation with status AWAIT_CONFIRMATION
    WHEN  confirm() is called
    THEN  status transitions to PENDING
    """
    biometric = BiometricValidation.create(
        application_id=UUID(int=1),
        provider_id="profile-123",
        provider="idwall",
    )

    biometric.confirm()

    assert biometric.status == BiometricValidationStatus.PENDING


def test_given_biometric_when_block_called_then_status_is_blocked() -> None:
    """
    GIVEN a BiometricValidation with status AWAIT_CONFIRMATION
    WHEN  block() is called
    THEN  status transitions to BLOCKED
    """
    biometric = BiometricValidation.create(
        application_id=UUID(int=1),
        provider_id="profile-123",
        provider="idwall",
    )

    biometric.block()

    assert biometric.status == BiometricValidationStatus.BLOCKED


def test_given_biometric_when_complete_called_then_status_is_completed() -> None:
    """
    GIVEN a BiometricValidation with status AWAIT_CONFIRMATION
    WHEN  complete() is called
    THEN  status transitions to COMPLETED
    """
    biometric = BiometricValidation.create(
        application_id=UUID(int=1),
        provider_id="profile-123",
        provider="idwall",
    )

    biometric.complete()

    assert biometric.status == BiometricValidationStatus.COMPLETED


def test_given_biometric_when_status_changes_then_step_execution_status_matches() -> (
    None
):
    """
    GIVEN a BiometricValidation with an attached step execution
    WHEN  its status changes
    THEN  step_execution status is updated to the current entity status
    """
    biometric = BiometricValidation.create(
        application_id=UUID(int=1),
        provider_id="profile-123",
        provider="idwall",
    )

    biometric.confirm()
    assert biometric.step_execution is not None
    assert biometric.step_execution.status == BiometricValidationStatus.PENDING

    biometric.block()
    assert biometric.step_execution.status == BiometricValidationStatus.BLOCKED

    biometric.complete()
    assert biometric.step_execution.status == BiometricValidationStatus.COMPLETED


def test_given_entities_package_when_importing_then_biometric_symbols_are_exported() -> (
    None
):
    """
    GIVEN the chatbot.domain.entities package
    WHEN  BiometricValidation and BiometricValidationStatus are imported from it
    THEN  both symbols are exported and usable
    """
    assert BiometricValidation.__name__ == "BiometricValidation"
    assert BiometricValidationStatus.AWAIT_CONFIRMATION == "AWAIT_CONFIRMATION"
