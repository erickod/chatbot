from chatbot.domain.entities.caller import Caller


class SaveCallerRepository:
    async def create(self, caller: Caller) -> None: ...
