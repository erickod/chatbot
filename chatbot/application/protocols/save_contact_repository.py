from chatbot.domain.entities.application_contact import ApplicationContact


class SaveContactRepository:
    async def run(self, contact: ApplicationContact) -> None: ...
