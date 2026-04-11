from chatbot.domain.entities.caller import Caller


class SaveCallerRepository:
    async def run(self, caller: Caller) -> None: ...
