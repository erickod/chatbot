from uuid import UUID

from pydantic import BaseModel

from chatbot.application.protocols.application_repository import ApplicationRepository
from chatbot.application.protocols.save_biometric_validation_repository import (
    BiometricValidationRepository,
)


class Input(BaseModel):
    provider_id: str
    provider: str = "idwall"


class Output(BaseModel):
    id: UUID | None
    step_execution_id: UUID | None
    status: str
    message: str | None = None


class ProcessBiometricValidation:
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
        if biometric := await self._biometric_repo.load_by_provider_id(
            provider=input.provider, provider_id=input.provider_id
        ):
            if application := await self._application_repo.get_by_id(
                id=biometric.application_id
            ):
                biometric.complete()
                await self._biometric_repo.update(biometric)
                return Output(
                    id=biometric.id,
                    step_execution_id=biometric.step_execution.id,
                    status=biometric.status,
                )
        return Output(
            id=biometric.id,
            step_execution_id=biometric.step_execution.id,
            status=biometric.status,
        )
