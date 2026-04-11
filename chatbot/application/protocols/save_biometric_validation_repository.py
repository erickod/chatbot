from chatbot.domain.entities.biometric_validation import BiometricValidation


class SaveBiometricValidationRepository:
    async def run(self, biometric: BiometricValidation) -> None: ...
