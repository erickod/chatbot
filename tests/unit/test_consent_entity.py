from uuid import UUID

import pytest

from chatbot.domain.entities import Consent, ConsentStatus


def test_given_valid_args_when_create_then_status_is_pending() -> None:
    """
    GIVEN valid consent arguments
    WHEN  Consent.create() is called
    THEN  the returned instance has status PENDING
    """
    consent = Consent.create(application_id=UUID(int=1), terms_id=UUID(int=2))

    assert consent.status == ConsentStatus.PENDING


def test_given_valid_args_when_create_then_id_is_generated() -> None:
    """
    GIVEN valid consent arguments
    WHEN  Consent.create() is called
    THEN  the returned instance has a non-None UUID id
    """
    consent = Consent.create(application_id=UUID(int=1), terms_id=UUID(int=2))

    assert isinstance(consent.id, UUID)


def test_given_valid_args_when_create_then_timestamps_are_utc() -> None:
    """
    GIVEN valid consent arguments
    WHEN  Consent.create() is called
    THEN  created_at is timezone-aware and updated_at is None
    """
    consent = Consent.create(application_id=UUID(int=1), terms_id=UUID(int=2))

    assert consent.created_at.tzinfo is not None
    assert consent.updated_at is None


def test_given_valid_args_when_create_then_step_execution_is_attached() -> None:
    """
    GIVEN valid consent arguments
    WHEN  Consent.create() is called
    THEN  step_execution is set with matching id and application_id
    """
    consent = Consent.create(application_id=UUID(int=1), terms_id=UUID(int=2))

    assert consent.step_execution is not None
    assert consent.step_execution.id == consent.id
    assert consent.step_execution.application_id == consent.application_id


def test_given_valid_args_when_create_then_step_execution_name_is_consent() -> None:
    """
    GIVEN valid consent arguments
    WHEN  Consent.create() is called
    THEN  step_execution has name consent, matching status and is_final False
    """
    consent = Consent.create(application_id=UUID(int=1), terms_id=UUID(int=2))

    assert consent.step_execution is not None
    assert consent.step_execution.name == "consent"
    assert consent.step_execution.status == ConsentStatus.PENDING
    assert consent.step_execution.is_final is False


def test_given_consent_when_block_called_then_status_is_blocked() -> None:
    """
    GIVEN a Consent with status PENDING
    WHEN  block() is called
    THEN  status transitions to BLOCKED
    """
    consent = Consent.create(application_id=UUID(int=1), terms_id=UUID(int=2))

    consent.block()

    assert consent.status == ConsentStatus.BLOCKED


def test_given_consent_when_complete_called_then_status_is_completed() -> None:
    """
    GIVEN a Consent with status PENDING
    WHEN  complete() is called
    THEN  status transitions to COMPLETED
    """
    consent = Consent.create(application_id=UUID(int=1), terms_id=UUID(int=2))

    consent.complete()

    assert consent.status == ConsentStatus.COMPLETED


def test_given_consent_when_status_changes_then_step_execution_status_matches() -> None:
    """
    GIVEN a Consent with an attached step execution
    WHEN  its status changes
    THEN  step_execution status is updated to the current entity status
    """
    consent = Consent.create(application_id=UUID(int=1), terms_id=UUID(int=2))

    consent.block()
    assert consent.step_execution is not None
    assert consent.step_execution.status == ConsentStatus.BLOCKED

    consent.complete()
    assert consent.step_execution.status == ConsentStatus.COMPLETED


def test_given_entities_package_when_importing_then_consent_symbols_are_exported() -> (
    None
):
    """
    GIVEN the chatbot.domain.entities package
    WHEN  Consent and ConsentStatus are imported from it
    THEN  both symbols are exported and usable
    """
    assert Consent.__name__ == "Consent"
    assert ConsentStatus.PENDING == "PENDING"


def test_given_missing_required_arg_when_create_then_type_error_is_raised() -> None:
    """
    GIVEN Consent.create() requires all arguments
    WHEN  one required argument is omitted
    THEN  Python raises TypeError for the invalid call signature
    """
    with pytest.raises(TypeError):
        Consent.create(application_id=UUID(int=1))
