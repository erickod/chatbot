from chatbot.domain.entities import BiometricValidation
from chatbot.domain.entities.application_contact import ApplicationContact


class FakeBiometricValidationGateway:
    async def request_validation(
        self, validation: BiometricValidation, contact: ApplicationContact
    ) -> None:
        return
