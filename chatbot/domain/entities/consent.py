from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict, PrivateAttr

from .step_execution import StepExecution


class ConsentStatus(str, Enum):
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class Consent(BaseModel):
    id: UUID
    application_id: UUID
    terms_id: UUID
    status: ConsentStatus
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
    _step_execution: StepExecution | None = PrivateAttr()

    @classmethod
    def create(cls, application_id: UUID, terms_id: UUID) -> "Consent":
        now = datetime.now(timezone.utc)
        instance = cls(
            id=uuid7(),
            application_id=application_id,
            terms_id=terms_id,
            status=ConsentStatus.PENDING,
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
            name="consent",
            status=self.status,
            is_final=False,
        )

    def block(self) -> None:
        self.status = ConsentStatus.BLOCKED
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    def complete(self) -> None:
        self.status = ConsentStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
