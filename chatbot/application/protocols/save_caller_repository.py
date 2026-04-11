from chatbot.domain.entities.caller import Caller


class CallerRepository:
    async def create(self, caller: Caller) -> None: ...
