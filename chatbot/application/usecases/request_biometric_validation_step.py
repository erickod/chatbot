from uuid import UUID

from pydantic import BaseModel

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.application.protocols.save_biometric_validation_repository import (
    BiometricValidationRepository,
)
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
    ) -> None:
        self._biometric_repo = biometric_repo
        self._application_repo = application_repo

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
        biometric = BiometricValidation.create(
            application_id=application.id,
            provider_id=input.provider_id,
            provider=input.provider,
        )
        application.advance_step(biometric.step_execution)
        await self._biometric_repo.create(biometric)
        return Output(
            id=biometric.id,
            step_execution_id=biometric.step_execution.id,
            status=biometric.status,
        )
