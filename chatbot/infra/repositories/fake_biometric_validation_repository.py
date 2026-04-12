from uuid import UUID

from chatbot.domain.entities.biometric_validation import BiometricValidation


class FakeBiometricValidationRepository:
    def __init__(self, seed: list[BiometricValidation] = []) -> None:
        self.by_id: dict[UUID, BiometricValidation] = {}
        self.by_provider_id: dict[tuple[str, str], BiometricValidation] = {}
        self._process_seed(seed)

    def _process_seed(self, seed: list[BiometricValidation]) -> None:
        for item in seed:
            self.by_id[item.id] = item
            self.by_provider_id[(item.provider, item.provider_id)] = item

    async def create(self, biometric: BiometricValidation) -> None:
        self._process_seed([biometric])

    async def load_by_provider_id(
        self, provider: str, provider_id: str
    ) -> BiometricValidation | None:
        return self.by_provider_id.get((provider, provider_id))

    async def update(self, biometric: BiometricValidation) -> None:
        self._process_seed([biometric])
