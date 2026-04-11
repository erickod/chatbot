from chatbot.application.protocols.save_originator_seller_repository import (
    SaveOriginatorSellerRepository,
)
from chatbot.domain.entities.originator_seller import OriginatorSeller
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBOriginatorSeller, DBStepExecution


class SASaveOriginatorSellerRepository(BaseRepository, SaveOriginatorSellerRepository):
    async def run(self, seller: OriginatorSeller) -> None:
        step = seller.step_execution
        self.db_session.add(
            DBOriginatorSeller(
                id=seller.id,
                application_id=seller.application_id,
                name=seller.name,
                email=seller.email,
                national_id=seller.national_id.value,
                position=seller.position,
                status=seller.status,
            )
        )
        self.db_session.add(
            DBStepExecution(
                id=step.id,
                application_id=step.application_id,
                name=step.name,
                status=str(step.status),
                data=step.data,
            )
        )
