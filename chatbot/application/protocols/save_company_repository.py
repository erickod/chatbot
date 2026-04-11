from chatbot.domain.entities.customer import Customer


class CompanyRepository:
    async def create(self, customer: Customer) -> None: ...
