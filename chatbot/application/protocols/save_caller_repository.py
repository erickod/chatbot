from typing import Protocol

from chatbot.domain.entities.caller import Caller


class CallerRepository(Protocol):
    async def create(self, caller: Caller) -> None: ...
