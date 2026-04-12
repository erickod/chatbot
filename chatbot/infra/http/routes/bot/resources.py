import logging
from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from opentelemetry import trace
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.application.services.usecase_registry import (
    StateLoaderRegistry,
    UseCaseRegistry,
)
from chatbot.application.usecases.load_caller import LoadCaller
from chatbot.application.usecases.request_payment_step import RequestPaymentStep
from chatbot.application.usecases.save_caller_step import SaveNameStep
from chatbot.application.usecases.save_cnpj_step import SaveCnpjStep
from chatbot.application.usecases.save_consent_step import SaveTermsStep
from chatbot.application.usecases.save_contact_step import SaveContactStep
from chatbot.application.usecases.start_application_step import StartApplicationStep
from chatbot.domain.entities.application import Application
from chatbot.infra.db.postgres import get_session
from chatbot.infra.external_services.starkbank_pix_gateway import (
    StarkbankPixGatewayAdapter,
)
from chatbot.infra.repositories.fake_application_repository import (
    FakeApplicationRepository,
)
from chatbot.infra.repositories.fake_caller_repository import FakeCallerRepository
from chatbot.infra.repositories.fake_company_repository import FakeCompanyRepository
from chatbot.infra.repositories.fake_consent_repository import FakeConsentRepository
from chatbot.infra.repositories.fake_contact_repository import FakeContactRepository
from chatbot.infra.repositories.fake_document_repository import FakeDocumentRepository
from chatbot.infra.repositories.fake_payment_repository import FakePaymentRepository
from chatbot.infra.repositories.sa_application_repository import SAApplicationRepository
from chatbot.infra.repositories.save_caller_repository import SACallerRepository

logger: logging.Logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

router = APIRouter(tags=["bot"])


class UpdateStepIn(BaseModel):
    current_step: str
    bot_user_id: str = ""
    conversation_id: str = ""
    data: dict[str, str] = Field(default_factory=dict)


caller_repo = FakeCallerRepository()
# Application deve ser criado no load dos steps
application_repo = FakeApplicationRepository(
    direct_return=Application.create(
        originator_code=UUID("e2829968-71af-40d7-84b9-03807439ff15"),
        originator_phone="lend300",
        company_phone="lend300_test_chat-uIir5y9kT3NNPf5y0S2VOKExMrh1",
    )
)
company_repo = FakeCompanyRepository()
consent_repo = FakeConsentRepository()
contact_repo = FakeContactRepository()
payment_repo = FakePaymentRepository()
document_repo = FakeDocumentRepository()


@router.post("/bot/update_step", response_model=None, status_code=HTTPStatus.OK)
@router.post("/chatbot/update_step", response_model=None, status_code=HTTPStatus.OK)
async def update_step_bot(
    payload: UpdateStepIn, db_session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    application_repo = SAApplicationRepository(db_session)
    caller_repo = SACallerRepository(db_session)
    payload.data = {
        k.replace(f"{payload.current_step}_", ""): v for k, v in payload.data.items()
    }
    registry = UseCaseRegistry()
    registry.register_step(
        SaveNameStep(caller_repo=caller_repo, application_repo=application_repo)
    )
    registry.register_step(
        SaveCnpjStep(application_repo=application_repo, company_repo=company_repo)
    )
    registry.register_step(
        SaveCnpjStep(application_repo=application_repo, company_repo=company_repo)
    )
    registry.register_step(
        SaveTermsStep(
            application_repository=application_repo, consent_repository=consent_repo
        )
    )
    registry.register_step(
        SaveContactStep(application_repo=application_repo, contact_repo=contact_repo)
    )
    registry.register_step(
        RequestPaymentStep(
            payment_repo=payment_repo,
            application_repo=application_repo,
            contact_repo=contact_repo,
            payment_gateway=StarkbankPixGatewayAdapter(),
        )
    )
    if output := await registry.run(payload.data, name=payload.current_step):
        # TODO: handle convertions inside each output dto - not on dict compreehension
        return JSONResponse(
            {k: v and str(v) or v for k, v in output.model_dump(mode="json").items()}
        )
    return JSONResponse({"error": "unknown step"}, status_code=HTTPStatus.BAD_REQUEST)


@router.get("/bot/session", status_code=HTTPStatus.OK)
@router.get("/chatbot/session", status_code=HTTPStatus.OK)
async def restore_session(
    originator_phone: str,
    company_phone: str,
    db_session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    caller_repo = SACallerRepository(db_session)
    registry = StateLoaderRegistry()
    registry.register_step(
        StartApplicationStep(application_repository=SAApplicationRepository(db_session))
    )
    registry.register_step(LoadCaller(caller_repo=caller_repo))
    steps = await registry.run(
        dict(originator_phone=originator_phone, company_phone=company_phone)
    )
    response: dict[str, Any] = {
        "steps": [
            cast(BaseModel, handler).model_dump(mode="json") for handler in steps
        ],
    }
    return JSONResponse(response)
