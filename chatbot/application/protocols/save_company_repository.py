from typing import Protocol

from chatbot.domain.entities.customer import Customer


class CompanyRepository(Protocol):
    async def create(self, customer: Customer) -> None: ...
    async def load_by_phones(
        self, originator_phone: str, company_phone: str
    ) -> Customer | None: ...
