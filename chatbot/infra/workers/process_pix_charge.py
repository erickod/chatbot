from datetime import datetime
from typing import Any, Callable, Coroutine

from hermes.pubsub.consumer import PubSubConsumer
from pydantic import BaseModel

from chatbot.application.protocols.save_payment_repository import PaymentRepository
from chatbot.application.usecases.confirm_payment import ConfirmPayment, Input
from chatbot.infra.db.postgres import create_thread_safe_context
from chatbot.settings import settings


class ProcessPixChargeMessage(BaseModel):
    qr_code_id: str
    amount: int
    deposited_at: datetime
    national_id: str | None
    name: str | None = None


class ProcessPixChargeMetadata(BaseModel):
    bank_code: str
    branch_code: str
    account_number: str
    account_type: str
    status: str
    transaction_ids: list[str]


class ProcessPixChargeMessageEnvelope(BaseModel):
    message: ProcessPixChargeMessage
    metadata: ProcessPixChargeMetadata


def get_callback(
    payment_repo: PaymentRepository,
) -> Callable[
    [str, dict[str, str | bytes], ProcessPixChargeMessageEnvelope],
    Coroutine[Any, Any, None],
]:
    async def callback(
        message_id: str,
        attributes: dict[str, str | bytes],
        message: ProcessPixChargeMessageEnvelope,
    ) -> None:
        input = Input(reference=message.message.qr_code_id)
        output = await ConfirmPayment(payment_repo=payment_repo).execute(input)
        print(output)

    return callback


def process(payment_repo: PaymentRepository) -> None:
    create_thread_safe_context(is_single_threaded=True)
    consumer = PubSubConsumer(
        project_id=settings.PROJECT_ID,
        subscription_id=settings.PROCESS_PIX_CHARGE_WEBHOOK_SUB_NAME,
        message_model=ProcessPixChargeMessageEnvelope,
        max_messages=settings.MAX_MESSAGES,
    )
    consumer.run(get_callback(payment_repo=payment_repo))  # type: ignore
