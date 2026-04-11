from uuid import UUID

from chatbot.application.usecases.register_originator_seller import (
    Input as RegisterOriginatorInput,
)
from chatbot.application.usecases.register_originator_seller import (
    RegisterOriginatorSellerStep,
)
from chatbot.application.usecases.save_cnpj_step import Input as SaveCnpjStepInput
from chatbot.application.usecases.save_cnpj_step import SaveCnpjStep
from chatbot.application.usecases.save_consent_step import (
    Input as SaveConsentStepInput,
)
from chatbot.application.usecases.save_consent_step import (
    SaveConsentStep,
)
from chatbot.application.usecases.save_contact_step import Input as SaveContactStepInput
from chatbot.application.usecases.save_contact_step import SaveContactStep
from chatbot.application.usecases.start_application_step import (
    Input as StartApplicationInput,
)
from chatbot.application.usecases.start_application_step import StartApplicationStep
from chatbot.domain.entities.application import ApplicationStatus
from chatbot.domain.entities.application_contact import ContactStatus
from chatbot.domain.entities.consent import ConsentStatus
from chatbot.domain.entities.customer import CustomerStatus
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_company_repository import FakeCompanyRepository
from chatbot.infra.repositories.fake_consent_repository import FakeConsentRepository
from chatbot.infra.repositories.fake_contact_repository import FakeContactRepository
from chatbot.infra.repositories.fake_originator_repository import (
    FakeOriginatorRepository,
)


async def test_kyc_flow_with_seller_successfully() -> None:
    ########## REPOSITORIES ##########
    originator_repo = FakeOriginatorRepository()
    application_repo = FakeApplicationRepository()
    company_repo = FakeCompanyRepository()
    consent_repo = FakeConsentRepository()
    contact_repo = FakeContactRepository()

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
    sut = RegisterOriginatorSellerStep(originator_repository=originator_repo)
    register_originator_output = await sut.execute(register_originator_input)
    assert (
        register_originator_output.id
        == originator_repo.by_id[register_originator_output.id].id
    )

    ########## START Application ##########
    start_application_input = StartApplicationInput(
        originator_phone=originator_phone, company_phone=company_phone
    )
    sut = StartApplicationStep(application_repository=application_repo)
    start_application_output = await sut.execute(start_application_input)
    assert (
        start_application_output.id
        == application_repo.by_id[start_application_output.id].id
    )
    assert start_application_output.status == ApplicationStatus.PENDING

    ########## Fill CNPJ ##########
    save_cnpj_input = SaveCnpjStepInput(
        originator_phone=originator_phone,
        company_phone=company_phone,
        national_id="23368630000119",
    )
    sut = SaveCnpjStep(application_repo=application_repo, company_repo=company_repo)
    save_cnpj_output = await sut.execute(save_cnpj_input)
    saved_company = company_repo.by_id[save_cnpj_output.id]
    assert saved_company.status == save_cnpj_output.status == CustomerStatus.COMPLETED
    assert saved_company.application_id == start_application_output.id

    ########## SaveConsent ##########
    save_consent_input = SaveConsentStepInput(
        originator_phone=originator_phone,
        company_phone=company_phone,
        status="ACCEPTED",
    )
    sut = SaveConsentStep(
        consent_repository=consent_repo,
        application_repository=application_repo,
    )
    save_consent_output = await sut.execute(save_consent_input)
    saved_consent = consent_repo.by_id[save_consent_output.id]
    assert saved_consent.status == save_consent_output.status == ConsentStatus.COMPLETED
    assert saved_consent.application_id == start_application_output.id

    ########## SaveContact ##########
    save_contact_input = SaveContactStepInput(
        originator_phone=originator_phone,
        company_phone=company_phone,
    )
    sut = SaveContactStep(application_repo=application_repo, contact_repo=contact_repo)
    save_contact_output = await sut.execute(save_contact_input)
    saved_contact = contact_repo.by_id[save_contact_output.id]
    assert saved_contact.status == save_contact_output.status == ContactStatus.COMPLETED
    assert saved_contact.application_id == start_application_output.id
