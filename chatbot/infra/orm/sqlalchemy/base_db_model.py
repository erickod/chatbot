import uuid
from datetime import datetime
from uuid import UUID

from chatbot.infra.db.postgres.base import Base
from chatbot.infra.db.postgres.functions import utcnow
from sqlalchemy import DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        postgresql.UUID, primary_key=True, default=uuid.uuid7
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=utcnow()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=utcnow()
    )
