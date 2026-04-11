from chatbot.domain.entities.originator_seller import OriginatorSeller


class SaveOriginatorSellerRepository:
    async def run(self, seller: OriginatorSeller) -> None: ...
