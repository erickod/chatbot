from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict, PrivateAttr

from .step_execution import StepExecution


class OriginatorSellerStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"


class OriginatorSeller(BaseModel):
    id: UUID
    application_id: UUID | None
    name: str
    email: str
    position: str
    status: OriginatorSellerStatus
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
    _step_execution: StepExecution | None = PrivateAttr()

    @classmethod
    def create(
        cls,
        *,
        name: str,
        email: str,
        position: str,
        application_id: UUID | None = None,
    ) -> "OriginatorSeller":
        now = datetime.now(timezone.utc)
        instance = cls(
            id=uuid7(),
            application_id=application_id,
            name=name,
            email=email,
            position=position,
            status=OriginatorSellerStatus.COMPLETED,
            created_at=now,
            updated_at=None,
        )
        instance._attach_step_execution()
        return instance

    def _attach_step_execution(self) -> None:
        if not self.application_id:
            return
        self._step_execution = StepExecution(
            id=self.id,
            application_id=self.application_id,
            created_at=self.created_at,
            name="seller",
            status=self.status,
            data={
                "name": self.name,
                "email": self.email,
                "position": self.position,
            },
            is_final=False,
        )

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
