from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict, PrivateAttr

from .step_execution import StepExecution


class BiometricValidationStatus(str, Enum):
    AWAIT_CONFIRMATION = "AWAIT_CONFIRMATION"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class BiometricValidation(BaseModel):
    id: UUID
    application_id: UUID
    provider: str
    provider_id: str
    status: BiometricValidationStatus
    validation_result: dict
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
    _step_execution: StepExecution | None = PrivateAttr()

    @classmethod
    def create(
        cls,
        application_id: UUID,
        provider: str,
        provider_id: str,
    ) -> "BiometricValidation":
        now = datetime.now(timezone.utc)
        instance = cls(
            id=uuid7(),
            application_id=application_id,
            provider=provider,
            provider_id=provider_id,
            status=BiometricValidationStatus.AWAIT_CONFIRMATION,
            validation_result={},
            created_at=now,
            updated_at=None,
        )
        instance._attach_step_execution()
        return instance

    def _attach_step_execution(self) -> None:
        self._step_execution = StepExecution(
            id=self.id,
            application_id=self.application_id,
            created_at=self.created_at,
            name="biometric",
            status=self.status,
            is_final=False,
        )

    def confirm(self) -> None:
        self.status = BiometricValidationStatus.PENDING
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    def block(self) -> None:
        self.status = BiometricValidationStatus.BLOCKED
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    def complete(self) -> None:
        self.status = BiometricValidationStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
