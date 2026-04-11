from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, PrivateAttr

from chatbot.domain.entities.step_execution import StepExecution
from chatbot.domain.value_objects.cnpj_national_id import CNPJNationalID


class CustomerStatus(str, Enum):
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class Customer(BaseModel):
    id: UUID
    application_id: UUID
    national_id: CNPJNationalID
    status: CustomerStatus
    created_at: datetime
    updated_at: datetime
    _step_execution: StepExecution | None = PrivateAttr()

    @classmethod
    def create(cls, national_id: str, application_id: UUID) -> "Customer":
        now = datetime.now(tz=timezone.utc)
        instance = cls(
            id=uuid7(),
            application_id=application_id,
            national_id=CNPJNationalID(value=national_id),
            status=CustomerStatus.COMPLETED,
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
            name="cnpj",
            status=self.status,
            data={"national_id": self.national_id.value},
            is_final=False,
        )

    def block(self) -> None:
        self.status = CustomerStatus.BLOCKED
        self._attach_step_execution()

    def complete(self) -> None:
        self.status = CustomerStatus.COMPLETED
        self._attach_step_execution()

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
