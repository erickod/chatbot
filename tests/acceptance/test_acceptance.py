from uuid import UUID

from chatbot.application.usecases.register_originator_seller import (
    Input as RegisterOriginatorInput,
)
from chatbot.application.usecases.register_originator_seller import (
    RegisterOriginatorSellerStep,
)
from chatbot.application.usecases.save_cnpj_step import Input as SaveCnpjStepInput
from chatbot.application.usecases.save_cnpj_step import SaveCnpjStep
from chatbot.application.usecases.start_application_step import (
    Input as StartApplicationInput,
)
from chatbot.application.usecases.start_application_step import StartApplicationStep
from chatbot.domain.entities.application import ApplicationStatus
from chatbot.domain.entities.customer import CustomerStatus
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_company_repository import FakeCompanyRepository
from chatbot.infra.repositories.fake_originator_repository import (
    FakeOriginatorRepository,
)


async def test_kyc_flow_with_seller_successfully() -> None:
    ########## REPOSITORIES ##########
    originator_repository = FakeOriginatorRepository()
    application_repository = FakeApplicationRepository()
    company_repository = FakeCompanyRepository()

    ########## PARMS ##########
    originator_phone: str = "ophone"
    company_phone: str = "cphone"

    register_originator_input = RegisterOriginatorInput(
        originator_phone=originator_phone,
        originator_code=UUID("f9e8dc07-6386-4976-a052-e6afcce2cb0c"),
        seller_phone="sphone",
        national_id="09888482000132",
        seller_name="Seller",
        seller_email="mail@mail.com",
    )
    sut = RegisterOriginatorSellerStep(originator_repository=originator_repository)
    register_originator_output = await sut.execute(register_originator_input)
    assert (
        register_originator_output.id
        == originator_repository.by_id[register_originator_output.id].id
    )

    ########## START Application ##########
    start_application_input = StartApplicationInput(
        originator_phone=originator_phone, company_phone=company_phone
    )
    sut = StartApplicationStep(application_repository=application_repository)
    start_application_output = await sut.execute(start_application_input)
    assert (
        start_application_output.id
        == application_repository.by_id[start_application_output.id].id
    )
    assert start_application_output.status == ApplicationStatus.PENDING

    ########## Fill CNPJ ##########
    save_cnpj_input = SaveCnpjStepInput(
        originator_phone=originator_phone,
        company_phone=company_phone,
        national_id="23368630000119",
    )
    sut = SaveCnpjStep(
        application_repo=application_repository, company_repo=company_repository
    )
    save_cnpj_inputoutput = await sut.execute(save_cnpj_input)
    assert (
        save_cnpj_inputoutput.id
        == company_repository.by_id[save_cnpj_inputoutput.id].id
    )
    assert save_cnpj_inputoutput.status == CustomerStatus.COMPLETED
