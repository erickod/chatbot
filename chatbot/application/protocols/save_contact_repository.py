from chatbot.domain.entities.application_contact import ApplicationContact


class ContactRepository:
    async def create(self, contact: ApplicationContact) -> None: ...
