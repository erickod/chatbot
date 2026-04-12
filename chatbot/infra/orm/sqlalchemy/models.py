from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from chatbot.domain.entities.application import ApplicationStatus
from chatbot.domain.entities.customer import CustomerStatus
from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from .base_db_model import BaseModel


class DBApplication(BaseModel):
    __tablename__ = "application"

    registration_id: Mapped[str | None] = mapped_column(
        String, nullable=True, unique=True
    )
    originator_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    company_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        String, nullable=False, server_default="IN_PROGRESS"
    )
    current_step: Mapped[str | None] = mapped_column(String, nullable=True)
    originator_code: Mapped[UUID | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    __table_args__ = (
        UniqueConstraint(
            "originator_phone",
            "company_phone",
            name="uq_originator_phone_company_phone",
        ),
    )


class DocumentEligibilityStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class DBOApplicationDocument(BaseModel):
    __tablename__ = "application_document"

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    document_type: Mapped[str] = mapped_column(String, nullable=False)
    document: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, server_default="COMPLETED"
    )


class DBOnboardingApplicationContact(BaseModel):
    __tablename__ = "application_contact"

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    cpf: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)


class DBOriginatorSeller(BaseModel):
    __tablename__ = "originator_seller"

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    national_id: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, server_default="COMPLETED"
    )


class DBPixCharge(BaseModel):
    __tablename__ = "pix_charge"

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("application.id", ondelete="RESTRICT"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String, nullable=False)
    provider_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    transaction_id: Mapped[str | None] = mapped_column(String, nullable=True)
    amount_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, server_default="BRL")
    qr_code_text: Mapped[str | None] = mapped_column(String, nullable=True)
    qr_code_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(nullable=True)


class BiometricValidationStatus(str, Enum):
    AWAIT_CONFIRMATION = "AWAIT_CONFIRMATION"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class DBBiometricValidation(BaseModel):
    __tablename__ = "biometric_validation"

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("application.id", ondelete="RESTRICT"), nullable=False
    )
    provider_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
        server_default="AWAIT_CONFIRMATION",
    )
    validation_result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)


class ConsentStatus(str, Enum):
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class DBTerms(BaseModel):
    __tablename__ = "terms"

    version: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    link: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )


class DBConsent(BaseModel):
    __tablename__ = "application_consent"

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("application.id", ondelete="CASCADE"), nullable=False
    )
    terms_id: Mapped[UUID] = mapped_column(
        ForeignKey("terms.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, server_default="PENDING"
    )


class DBStepExecution(BaseModel):
    __tablename__ = "step_execution"
    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("application.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    __table_args__ = (
        UniqueConstraint("application_id", "name", name="uq_step_execution_app_step"),
    )


class DBCustomer(BaseModel):
    __tablename__ = "customer"
    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("application.id", ondelete="CASCADE"), nullable=False
    )
    national_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    trading_name: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[CustomerStatus] = mapped_column(String, nullable=False)
