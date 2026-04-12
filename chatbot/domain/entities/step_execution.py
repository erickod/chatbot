from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class StepExecution(BaseModel):
    id: UUID
    application_id: UUID
    finished_at: datetime | None = None
    created_at: datetime
    status: str
    name: str
    data: dict[str, Any] = {}
    is_final: bool

    @property
    def started_at(self) -> datetime:
        return self.created_at

    @property
    def is_completed(self) -> bool:
        return self.status == "COMPLETED"
