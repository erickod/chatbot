from uuid import UUID

from pydantic import BaseModel, EmailStr

from chatbot.application.protocols.originator_repository import OriginatorRepository
from chatbot.domain.entities.originator import Originator
from chatbot.domain.entities.originator_seller import (
    OriginatorSeller,
)


class Input(BaseModel):
    originator_code: UUID
    originator_phone: str
    national_id: str
    seller_phone: str
    seller_name: str
    seller_email: EmailStr


class Output(BaseModel):
    id: UUID | None = None
    national_id: str | None = None
    step_name: str


class RegisterOriginatorSellerStep:
    input_schema: type[Input] = Input
    output_schema: type[Output] = Output

    def __init__(self, *, originator_repository: OriginatorRepository) -> None:
        self.originator_repository = originator_repository

    async def execute(self, input: Input) -> Output:
        seller = OriginatorSeller.create(
            name=input.seller_name, email=str(input.seller_email), position=""
        )
        originator = Originator.create(
            name=input.seller_name,
            email=input.seller_name,
            national_id=input.national_id,
            id=input.originator_code,
        )
        originator.config_seller(seller)
        await self.originator_repository.create(originator)
        return Output(
            id=originator.id,
            national_id=originator.national_id.value,
            step_name=self.__class__.__name__,
        )
