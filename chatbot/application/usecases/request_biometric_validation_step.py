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


class BiometricStepInput(BaseModel):
    originator_phone: str
    company_phone: str
    profile_ref: str
    validation_result: dict


class BiometricStepOutput(BaseModel):
    id: UUID | None
    step_execution_id: UUID | None
    status: str
    message: str | None = None


class RequestBiometricValidationStep:
    input_schema: type[BiometricStepInput] = BiometricStepInput
    output_schema: type[BiometricStepOutput] = BiometricStepOutput
    name: str = "biometric"

    def __init__(
        self,
        save_biometric_repo: BiometricValidationRepository,
        load_application_repo: ApplicationRepository,
    ) -> None:
        self._save_biometric_repo = save_biometric_repo
        self._load_application_repo = load_application_repo

    async def execute(self, input: BiometricStepInput) -> BiometricStepOutput:
        application = await self._load_application_repo.get_by_phones(
            originator_phone=input.originator_phone,
            company_phone=input.company_phone,
        )
        if not application:
            return BiometricStepOutput(
                id=None,
                step_execution_id=None,
                status=BiometricValidationStatus.BLOCKED,
                message="Application not found",
            )
        biometric = BiometricValidation.create(
            application_id=application.id,
            profile_ref=input.profile_ref,
            validation_result=input.validation_result,
        )
        application.advance_step(biometric.step_execution)
        await self._save_biometric_repo.create(biometric)
        return BiometricStepOutput(
            id=biometric.id,
            step_execution_id=biometric.step_execution.id,
            status=biometric.status,
        )
