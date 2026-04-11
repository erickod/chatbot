from typing import Protocol

from chatbot.domain.entities.originator import Originator


class OriginatorRepository(Protocol):
    async def create(self, originator: Originator) -> None: ...
