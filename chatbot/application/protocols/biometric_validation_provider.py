from typing import Protocol

from chatbot.domain.entities import BiometricValidation
from chatbot.domain.entities.application_contact import ApplicationContact


class BiometricValidationGateway(Protocol):
    async def request_validation(
        self, validation: BiometricValidation, contact: ApplicationContact
    ) -> None: ...
