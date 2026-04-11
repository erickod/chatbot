from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict

from .step_execution import StepExecution


class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class Application(BaseModel):
    id: UUID
    status: ApplicationStatus
    originator_phone: str
    company_phone: str
    created_at: datetime
    updated_at: datetime
    originator_code: UUID | None = None
    applicant_national_id: str | None = None
    session_id: UUID | None = None
    completed_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        originator_phone: str,
        company_phone: str,
        originator_code: UUID | None = None,
        status: Literal[
            ApplicationStatus.PENDING, ApplicationStatus.IN_PROGRESS
        ] = ApplicationStatus.IN_PROGRESS,
    ) -> "Application":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid7(),
            status=status,
            originator_phone=originator_phone,
            company_phone=company_phone,
            originator_code=originator_code,
            created_at=now,
            updated_at=now,
        )

    @property
    def registration_id(self) -> UUID:
        return self.id

    def advance_step(self, step: StepExecution) -> None:
        self.status = ApplicationStatus.IN_PROGRESS
        if step.is_final and step.is_completed:
            self.status = ApplicationStatus.COMPLETED
        self.updated_at = step.finished_at or step.created_at
