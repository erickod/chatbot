from chatbot.domain.entities.customer import Customer


class SaveCompanyRepository:
    async def run(self, customer: Customer) -> None: ...
