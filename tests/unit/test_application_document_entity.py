from uuid import UUID

from chatbot.domain.entities.application_document import (
    ApplicationDocument,
    DocumentEligibilityStatus,
)
from chatbot.domain.value_objects import NationalIDType


def test_given_valid_args_when_create_then_status_is_completed():
    """
    GIVEN a valid application_id
    WHEN  ApplicationDocument.create() is called
    THEN  the returned instance has status COMPLETED
    """
    doc = ApplicationDocument.create(application_id=UUID(int=1))
    assert doc.status == DocumentEligibilityStatus.COMPLETED


def test_given_valid_args_when_create_then_id_is_generated():
    """
    GIVEN a valid application_id
    WHEN  ApplicationDocument.create() is called
    THEN  the returned instance has a non-None UUID id
    """
    doc = ApplicationDocument.create(application_id=UUID(int=1))
    assert isinstance(doc.id, UUID)


def test_given_valid_args_when_create_then_document_is_none():
    """
    GIVEN a valid application_id without document value
    WHEN  ApplicationDocument.create() is called
    THEN  the document field is None
    """
    doc = ApplicationDocument.create(application_id=UUID(int=1))
    assert doc.document is None


def test_given_document_when_block_called_then_status_is_blocked():
    """
    GIVEN an ApplicationDocument with status COMPLETED
    WHEN  block() is called
    THEN  status transitions to BLOCKED
    """
    doc = ApplicationDocument.create(application_id=UUID(int=1))
    doc.block()
    assert doc.status == DocumentEligibilityStatus.BLOCKED


def test_given_blocked_document_when_block_called_again_then_status_is_blocked():
    """
    GIVEN an ApplicationDocument with status BLOCKED
    WHEN  block() is called again
    THEN  status remains BLOCKED (idempotent)
    """
    doc = ApplicationDocument.create(application_id=UUID(int=1))
    doc.block()
    doc.block()
    assert doc.status == DocumentEligibilityStatus.BLOCKED


def test_given_valid_args_when_create_then_step_execution_is_attached():
    """
    GIVEN a valid application_id
    WHEN  ApplicationDocument.create() is called
    THEN  step_execution is set with matching id and application_id
    """
    doc = ApplicationDocument.create(application_id=UUID(int=1))
    assert doc.step_execution is not None
    assert doc.step_execution.id == doc.id
    assert doc.step_execution.application_id == doc.application_id


def test_given_valid_args_when_create_then_document_type_is_cnpj():
    """
    GIVEN a valid application_id
    WHEN  ApplicationDocument.create() is called
    THEN  document_type property returns NationalIDType.CNPJ
    """
    doc = ApplicationDocument.create(application_id=UUID(int=1))
    assert doc.document_type == NationalIDType.CNPJ
