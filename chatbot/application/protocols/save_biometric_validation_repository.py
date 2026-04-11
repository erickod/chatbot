from typing import Protocol

from chatbot.domain.entities.biometric_validation import BiometricValidation


class BiometricValidationRepository(Protocol):
    async def create(self, biometric: BiometricValidation) -> None: ...
