from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, PrivateAttr

from .step_execution import StepExecution


class NameStepStatus(str, Enum):
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class Caller(BaseModel):
    id: UUID
    application_id: UUID
    name: str
    status: NameStepStatus
    created_at: datetime
    updated_at: datetime
    _step_execution: StepExecution | None = PrivateAttr()

    @classmethod
    def create(cls, name: str, application_id: UUID) -> "Caller":
        now = datetime.now(tz=timezone.utc)
        instance = cls(
            name=name,
            id=uuid7(),
            application_id=application_id,
            status=NameStepStatus.COMPLETED,
            created_at=now,
            updated_at=now,
        )
        instance._attach_step_execution()
        return instance

    def _attach_step_execution(self) -> None:
        self._step_execution = StepExecution(
            id=self.id,
            application_id=self.application_id,
            created_at=self.created_at,
            name="name",
            status=self.status,
            is_final=False,
        )

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
