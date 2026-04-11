from typing import Protocol

from chatbot.domain.entities import Consent


class ConsentRepository(Protocol):
    async def create(self, consent: Consent) -> None: ...
