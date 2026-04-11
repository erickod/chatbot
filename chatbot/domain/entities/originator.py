from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from chatbot.domain.entities.originator_seller import OriginatorSeller
from chatbot.domain.value_objects import CNPJNationalID, CPFNationalID


class Originator(BaseModel):
    id: UUID
    name: str
    email: str
    national_id: CNPJNationalID | CPFNationalID
    seller: OriginatorSeller | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls, *, name: str, email: str, national_id: str, id: UUID
    ) -> "Originator":
        now = datetime.now(timezone.utc)
        instance = cls(
            id=id,
            name=name,
            email=email,
            national_id=CNPJNationalID(value=national_id),
            seller=None,
            created_at=now,
            updated_at=None,
        )
        return instance

    def config_seller(self, seller: OriginatorSeller) -> None:
        self.seller = seller
