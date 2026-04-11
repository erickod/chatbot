from uuid import UUID

import pytest

from chatbot.domain.entities import ApplicationContact, ContactStatus


def test_given_valid_args_when_create_then_status_is_completed() -> None:
    """
    GIVEN valid application contact arguments
    WHEN  ApplicationContact.create() is called
    THEN  the returned instance has status COMPLETED
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    assert contact.status == ContactStatus.COMPLETED


def test_given_valid_args_when_create_then_id_is_generated() -> None:
    """
    GIVEN valid application contact arguments
    WHEN  ApplicationContact.create() is called
    THEN  the returned instance has a non-None UUID id
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    assert isinstance(contact.id, UUID)


def test_given_valid_args_when_create_then_nullable_fields_are_preserved() -> None:
    """
    GIVEN valid application contact arguments with nullable fields set to None
    WHEN  ApplicationContact.create() is called
    THEN  the returned instance preserves None in nullable fields
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf=None,
        name=None,
        email=None,
        role=None,
    )

    assert contact.cpf is None
    assert contact.name is None
    assert contact.email is None
    assert contact.role is None


def test_given_valid_args_when_create_then_step_execution_is_attached() -> None:
    """
    GIVEN valid application contact arguments
    WHEN  ApplicationContact.create() is called
    THEN  step_execution is set with matching id and application_id
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    assert contact.step_execution is not None
    assert contact.step_execution.id == contact.id
    assert contact.step_execution.application_id == contact.application_id


def test_given_valid_args_when_create_then_step_execution_has_contact_name() -> None:
    """
    GIVEN valid application contact arguments
    WHEN  ApplicationContact.create() is called
    THEN  step_execution has name contact and is not final
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    assert contact.step_execution is not None
    assert contact.step_execution.name == "contact"
    assert contact.step_execution.status == ContactStatus.COMPLETED
    assert contact.step_execution.is_final is False


def test_given_contact_when_block_called_then_status_is_blocked() -> None:
    """
    GIVEN an ApplicationContact with status COMPLETED
    WHEN  block() is called with a message
    THEN  status transitions to BLOCKED
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    contact.block(message="reason")

    assert contact.status == ContactStatus.BLOCKED


def test_given_contact_when_block_called_then_step_execution_status_is_blocked() -> (
    None
):
    """
    GIVEN an ApplicationContact with an attached step execution
    WHEN  block() is called with a message
    THEN  step_execution status is updated to BLOCKED
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    contact.block(message="reason")

    assert contact.step_execution is not None
    assert contact.step_execution.status == ContactStatus.BLOCKED


def test_given_blocked_contact_when_block_called_again_then_status_is_blocked() -> None:
    """
    GIVEN an ApplicationContact with status BLOCKED
    WHEN  block() is called again
    THEN  status remains BLOCKED
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    contact.block(message="first reason")
    contact.block(message="second reason")

    assert contact.status == ContactStatus.BLOCKED


def test_given_entities_package_when_importing_then_contact_symbols_are_exported() -> (
    None
):
    """
    GIVEN the chatbot.domain.entities package
    WHEN  ApplicationContact and ContactStatus are imported from it
    THEN  both symbols are exported and usable
    """
    assert ApplicationContact.__name__ == "ApplicationContact"
    assert ContactStatus.COMPLETED == "COMPLETED"


def test_given_missing_required_arg_when_create_then_type_error_is_raised() -> None:
    """
    GIVEN ApplicationContact.create() requires all arguments
    WHEN  one required argument is omitted
    THEN  Python raises TypeError for the invalid call signature
    """
    with pytest.raises(TypeError):
        ApplicationContact.create(
            application_id=UUID(int=1),
            cpf="12345678900",
            name="Jane Doe",
            email="jane@example.com",
        )


def test_given_contact_when_created_with_str_cpf_then_cpf_is_str() -> None:
    """
    GIVEN valid application contact arguments with a string CPF
    WHEN  ApplicationContact.create() is called
    THEN  the cpf field is stored as a string
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    assert isinstance(contact.cpf, str)
    assert contact.cpf == "12345678900"


def test_given_contact_when_created_then_message_is_none() -> None:
    """
    GIVEN valid application contact arguments
    WHEN  ApplicationContact.create() is called
    THEN  the message field defaults to None
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    assert contact.message is None


def test_given_contact_when_blocked_with_message_then_message_stored() -> None:
    """
    GIVEN an ApplicationContact with status COMPLETED
    WHEN  block() is called with a specific message
    THEN  the message field stores the provided reason
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    contact.block(message="Application not found")

    assert contact.message == "Application not found"


def test_given_contact_when_blocked_with_message_then_step_exec_blocked() -> None:
    """
    GIVEN an ApplicationContact with an attached step execution
    WHEN  block() is called with a message
    THEN  the step_execution status reflects BLOCKED
    """
    contact = ApplicationContact.create(
        application_id=UUID(int=1),
        cpf="12345678900",
        name="Jane Doe",
        email="jane@example.com",
        role="owner",
    )

    contact.block(message="Application not found")

    assert contact.step_execution is not None
    assert contact.step_execution.status == ContactStatus.BLOCKED
