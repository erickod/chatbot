from uuid import UUID

from chatbot.domain.entities.biometric_validation import BiometricValidation


class FakeBiometricValidationRepository:
    def __init__(self, seed: list[BiometricValidation] = []) -> None:
        self.by_id: dict[UUID, BiometricValidation] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[BiometricValidation]) -> None:
        for item in seed:
            self.by_id[item.id] = item

    async def create(self, biometric: BiometricValidation) -> None:
        self._process_seed([biometric])
