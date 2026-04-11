from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict, PrivateAttr

from .step_execution import StepExecution


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    AWAIT_CONFIRMATION = "AWAIT_CONFIRMATION"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class Payment(BaseModel):
    id: UUID
    application_id: UUID
    national_id: str | None
    provider: str | None
    provider_id: str | None
    transaction_id: str | None
    amount_cents: int
    currency: str
    qr_code_text: str | None
    qr_code_uri: str | None
    status: PaymentStatus
    expires_at: datetime | None
    paid_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
    _step_execution: StepExecution | None = PrivateAttr()

    @classmethod
    def create(
        cls,
        application_id: UUID,
        amount_cents: int,
        qr_code_text: str | None,
        qr_code_uri: str | None,
        expires_at: datetime | None,
        national_id: str | None = None,
        provider: str | None = None,
        provider_id: str | None = None,
        transaction_id: str | None = None,
        currency: str = "BRL",
    ) -> "Payment":
        now = datetime.now(timezone.utc)
        instance = cls(
            id=uuid7(),
            application_id=application_id,
            national_id=national_id,
            provider=provider,
            provider_id=provider_id,
            transaction_id=transaction_id,
            amount_cents=amount_cents,
            currency=currency,
            qr_code_text=qr_code_text,
            qr_code_uri=qr_code_uri,
            status=PaymentStatus.AWAIT_CONFIRMATION,
            expires_at=expires_at,
            paid_at=None,
            cancelled_at=None,
            created_at=now,
            updated_at=None,
        )
        instance._attach_step_execution()
        return instance

    def register_gateway_reference(
        self,
        *,
        gateway: str,
        ref: str,
        transaction_id: str | None = None,
        qr_code_text: str | None = None,
        qr_code_uri: str | None = None,
        expires_at: datetime | None = None,
    ) -> None:
        if gateway != "starkbank":
            raise ValueError(f"Unsupported payment gateway: {gateway}")
        self.provider = gateway
        self.provider_id = ref
        self.transaction_id = transaction_id
        self.qr_code_text = qr_code_text
        self.qr_code_uri = qr_code_uri
        self.expires_at = expires_at
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    def _attach_step_execution(self) -> None:
        self._step_execution = StepExecution(
            id=self.id,
            application_id=self.application_id,
            created_at=self.created_at,
            name="payment",
            status=self.status,
            is_final=False,
        )

    def mark_paid(self) -> None:
        self.status = PaymentStatus.COMPLETED
        self.paid_at = datetime.now(timezone.utc)
        self.updated_at = self.paid_at
        if self._step_execution is not None:
            self._attach_step_execution()

    def cancel(self) -> None:
        self.status = PaymentStatus.BLOCKED
        self.cancelled_at = datetime.now(timezone.utc)
        self.updated_at = self.cancelled_at
        if self._step_execution is not None:
            self._attach_step_execution()

    def expire(self) -> None:
        self.status = PaymentStatus.BLOCKED
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
