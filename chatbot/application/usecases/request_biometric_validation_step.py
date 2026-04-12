from uuid import UUID

from pydantic import BaseModel

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.application.protocols.biometric_validation_provider import (
    BiometricValidationGateway,
)
from chatbot.application.protocols.save_biometric_validation_repository import (
    BiometricValidationRepository,
)
from chatbot.application.protocols.save_contact_repository import ContactRepository
from chatbot.domain.entities.biometric_validation import (
    BiometricValidation,
    BiometricValidationStatus,
)


class Input(BaseModel):
    originator_phone: str
    company_phone: str
    provider_id: str
    provider: str = "idwall"


class Output(BaseModel):
    id: UUID | None
    step_execution_id: UUID | None
    status: str
    message: str | None = None


class StartBiometricValidation:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output
    name: str = "biometric"

    def __init__(
        self,
        biometric_repo: BiometricValidationRepository,
        application_repo: ApplicationRepository,
        contact_repo: ContactRepository,
        biometric_validation_gateway: BiometricValidationGateway,
    ) -> None:
        self._biometric_repo = biometric_repo
        self._application_repo = application_repo
        self._contact_repo = contact_repo
        self._biometric_gateway = biometric_validation_gateway

    async def execute(self, input: Input) -> Output:
        application = await self._application_repo.get_by_phones(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
        )
        if not application:
            return Output(
                id=None,
                step_execution_id=None,
                status=BiometricValidationStatus.BLOCKED,
                message="Application not found",
            )
        contact = await self._contact_repo.load_by_application_id(id=application.id)
        biometric = BiometricValidation.create(
            application_id=application.id,
            provider_id=input.provider_id,
            provider=input.provider,
        )
        if biometric and contact:
            await self._biometric_gateway.request_validation(biometric, contact)
            application.advance_step(biometric.step_execution)
            await self._biometric_repo.create(biometric)
            return Output(
                id=biometric.id,
                step_execution_id=biometric.step_execution.id,
                status=biometric.status,
            )
        return Output(
            id=None, step_execution_id=None, status="ERROR", message="Contact not found"
        )
