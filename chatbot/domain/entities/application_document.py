from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict, PrivateAttr

from chatbot.domain.value_objects import NationalIDType

from .step_execution import StepExecution


class DocumentEligibilityStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class ApplicationDocument(BaseModel):
    id: UUID
    application_id: UUID
    document: str | None
    status: DocumentEligibilityStatus
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
    _step_execution: StepExecution | None = PrivateAttr()

    @property
    def document_type(self) -> NationalIDType:
        return NationalIDType.CNPJ

    @classmethod
    def create(
        cls,
        application_id: UUID,
        document: str | None = None,
    ) -> "ApplicationDocument":
        now = datetime.now(timezone.utc)
        instance = cls(
            id=uuid7(),
            application_id=application_id,
            document=document,
            status=DocumentEligibilityStatus.COMPLETED,
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
            name=NationalIDType.CNPJ.value.lower(),
            status=self.status,
            is_final=False,
        )

    def block(self) -> None:
        self.status = DocumentEligibilityStatus.BLOCKED

    @property
    def step_execution(self) -> StepExecution | None:
        return self._step_execution
