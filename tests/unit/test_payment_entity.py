from uuid import UUID

import pytest

from chatbot.domain.entities import Payment, PaymentStatus


def test_given_valid_args_when_create_then_status_is_await_confirmation() -> None:
    """
    GIVEN valid payment arguments
    WHEN  Payment.create() is called
    THEN  the returned instance has status AWAIT_CONFIRMATION
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    assert payment.status == PaymentStatus.AWAIT_CONFIRMATION


def test_given_valid_args_when_create_then_id_is_generated() -> None:
    """
    GIVEN valid payment arguments
    WHEN  Payment.create() is called
    THEN  the returned instance has a non-None UUID id
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    assert isinstance(payment.id, UUID)


def test_given_valid_args_when_create_then_nullable_fields_are_preserved() -> None:
    """
    GIVEN valid payment arguments with nullable fields set to None
    WHEN  Payment.create() is called
    THEN  the returned instance preserves None in nullable fields
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    assert payment.transaction_id is None
    assert payment.qr_code_text is None
    assert payment.qr_code_uri is None
    assert payment.expires_at is None
    assert payment.paid_at is None
    assert payment.cancelled_at is None


def test_given_valid_args_when_create_then_step_execution_is_attached() -> None:
    """
    GIVEN valid payment arguments
    WHEN  Payment.create() is called
    THEN  step_execution is set with matching id and application_id
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    assert payment.step_execution is not None
    assert payment.step_execution.id == payment.id
    assert payment.step_execution.application_id == payment.application_id


def test_given_valid_args_when_create_then_step_execution_has_payment_name() -> None:
    """
    GIVEN valid payment arguments
    WHEN  Payment.create() is called
    THEN  step_execution has name payment and is not final
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    assert payment.step_execution is not None
    assert payment.step_execution.name == "payment"
    assert payment.step_execution.status == PaymentStatus.AWAIT_CONFIRMATION
    assert payment.step_execution.is_final is False


def test_given_payment_when_mark_paid_called_then_status_is_completed() -> None:
    """
    GIVEN a Payment with status PENDING
    WHEN  approve() is called
    THEN  status transitions to COMPLETED
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    payment.approve()

    assert payment.status == PaymentStatus.COMPLETED


def test_given_payment_when_mark_paid_called_then_paid_at_is_set() -> None:
    """
    GIVEN a Payment with status PENDING
    WHEN  approve() is called
    THEN  paid_at is populated
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    payment.approve()

    assert payment.paid_at is not None


def test_given_payment_when_cancel_called_then_status_is_blocked() -> None:
    """
    GIVEN a Payment with status PENDING
    WHEN  cancel() is called
    THEN  status transitions to BLOCKED
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    payment.cancel()

    assert payment.status == PaymentStatus.BLOCKED


def test_given_payment_when_cancel_called_then_cancelled_at_is_set() -> None:
    """
    GIVEN a Payment with status PENDING
    WHEN  cancel() is called
    THEN  cancelled_at is populated
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    payment.cancel()

    assert payment.cancelled_at is not None


def test_given_payment_when_expire_called_then_status_is_blocked() -> None:
    """
    GIVEN a Payment with status PENDING
    WHEN  expire() is called
    THEN  status transitions to BLOCKED
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    payment.expire()

    assert payment.status == PaymentStatus.BLOCKED


def test_given_blocked_payment_when_cancel_called_again_then_status_is_blocked() -> (
    None
):
    """
    GIVEN a Payment with status BLOCKED
    WHEN  cancel() is called again
    THEN  status remains BLOCKED
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    payment.cancel()
    payment.cancel()

    assert payment.status == PaymentStatus.BLOCKED


def test_given_blocked_payment_when_expire_called_again_then_status_is_blocked() -> (
    None
):
    """
    GIVEN a Payment with status BLOCKED
    WHEN  expire() is called again
    THEN  status remains BLOCKED
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        provider="starkbank",
        provider_id="provider-123",
        transaction_id=None,
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    payment.expire()
    payment.expire()

    assert payment.status == PaymentStatus.BLOCKED


def test_given_entities_package_when_importing_then_payment_symbols_are_exported() -> (
    None
):
    """
    GIVEN the chatbot.domain.entities package
    WHEN  Payment and PaymentStatus are imported from it
    THEN  both symbols are exported and usable
    """
    assert Payment.__name__ == "Payment"
    assert PaymentStatus.PENDING == "PENDING"


def test_given_payment_when_gateway_reference_registered_then_provider_fields_update() -> (
    None
):
    """
    GIVEN a payment created in memory without gateway identifiers
    WHEN  register_gateway_reference() is called with StarkBank data
    THEN  provider and provider_id are stored on the entity
    """
    payment = Payment.create(
        application_id=UUID(int=1),
        amount_cents=1500,
        currency="BRL",
        qr_code_text=None,
        qr_code_uri=None,
        expires_at=None,
    )

    payment.register_gateway_reference(
        gateway="starkbank",
        ref="provider-123",
        transaction_id="txn-123",
        qr_code_text="000201",
        qr_code_uri="https://example.com/qr.png",
    )

    assert payment.provider == "starkbank"
    assert payment.provider_id == "provider-123"
    assert payment.transaction_id == "txn-123"


def test_given_missing_required_arg_when_create_then_type_error_is_raised() -> None:
    """
    GIVEN Payment.create() requires all arguments
    WHEN  one required argument is omitted
    THEN  Python raises TypeError for the invalid call signature
    """
    with pytest.raises(TypeError):
        Payment.create(
            application_id=UUID(int=1),
            provider="starkbank",
            provider_id="provider-123",
            transaction_id=None,
            amount_cents=1500,
            currency="BRL",
            qr_code_text=None,
            qr_code_uri=None,
        )
