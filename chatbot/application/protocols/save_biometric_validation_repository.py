from typing import Protocol

from chatbot.domain.entities.biometric_validation import BiometricValidation


class BiometricValidationRepository(Protocol):
    async def create(self, biometric: BiometricValidation) -> None: ...
    async def load_by_provider_id(
        self, provider: str, provider_id: str
    ) -> BiometricValidation | None: ...
    async def update(self, biometric: BiometricValidation) -> None: ...
