from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict, PrivateAttr

from .step_execution import StepExecution


class ContactStatus(str, Enum):
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class ApplicationContact(BaseModel):
    id: UUID
    application_id: UUID
    cpf: str | None
    name: str | None
    email: str | None
    role: str | None
    status: ContactStatus
    message: str | None = None
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
    _step_execution: StepExecution | None = PrivateAttr()

    @classmethod
    def create(
        cls,
        application_id: UUID,
        cpf: str | None,
        name: str | None,
        email: str | None,
        role: str | None,
    ) -> "ApplicationContact":
        now = datetime.now(timezone.utc)
        instance = cls(
            id=uuid7(),
            application_id=application_id,
            cpf=cpf,
            name=name,
            email=email,
            role=role,
            status=ContactStatus.COMPLETED,
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
            name="contact",
            status=self.status,
            is_final=False,
        )

    def block(self, message: str) -> None:
        self.status = ContactStatus.BLOCKED
        self.message = message
        if self._step_execution is not None:
            self._attach_step_execution()

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
