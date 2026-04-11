from typing import Protocol

from chatbot.domain.entities.customer import Customer


class CompanyRepository(Protocol):
    async def create(self, customer: Customer) -> None: ...
