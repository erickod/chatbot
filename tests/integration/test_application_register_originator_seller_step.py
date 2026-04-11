from uuid import uuid7

from chatbot.application.usecases.register_originator_seller import (
    Input,
    RegisterOriginatorSellerStep,
)
from chatbot.infra.repositories.fake_originator_repository import (
    FakeOriginatorRepository,
)


async def test_register_originator_with_its_seller() -> None:
    originator_repo = FakeOriginatorRepository()
    sut = RegisterOriginatorSellerStep(originator_repository=originator_repo)
    input = Input(
        originator_phone="originator_phone",
        originator_code=uuid7(),
        national_id="43571703000182",
        seller_phone="company_phone",
        seller_name="John Doe",
        seller_email="mail@mail.com",
    )
    output = await sut.execute(input)
    assert output.id
    assert originator_repo.by_id.values()
    assert originator_repo.by_id[output.id].seller
    assert originator_repo.by_id[output.id].seller.email == input.seller_email
    assert originator_repo.by_id[output.id].seller.name == input.seller_name
