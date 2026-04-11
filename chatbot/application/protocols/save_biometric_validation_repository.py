from chatbot.domain.entities.biometric_validation import BiometricValidation


class BiometricValidationRepository:
    async def create(self, biometric: BiometricValidation) -> None: ...
