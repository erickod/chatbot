from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict, PrivateAttr

from .step_execution import StepExecution


class ConsentStatus(str, Enum):
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class ConsentChoice(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


class Consent(BaseModel):
    id: UUID
    application_id: UUID
    term_id: UUID
    status: ConsentStatus
    choice: ConsentChoice
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
    _step_execution: StepExecution | None = PrivateAttr()

    @classmethod
    def create(cls, application_id: UUID, term_id: UUID) -> "Consent":
        now = datetime.now(timezone.utc)
        instance = cls(
            id=uuid7(),
            application_id=application_id,
            term_id=term_id,
            status=ConsentStatus.PENDING,
            choice=ConsentChoice.PENDING,
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

    def decline(self) -> None:
        self.status = ConsentStatus.BLOCKED
        self.choice = ConsentChoice.DECLINED
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    def accept(self) -> None:
        self.status = ConsentStatus.COMPLETED
        self.choice = ConsentChoice.ACCEPTED
        self.updated_at = datetime.now(timezone.utc)
        if self._step_execution is not None:
            self._attach_step_execution()

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
