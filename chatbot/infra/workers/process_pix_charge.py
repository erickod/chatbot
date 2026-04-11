import logging
from typing import Any, Callable, Coroutine

# TODO: this came from another project e must be adapted use PixCharge Entity
import settings
from chatbot.app.onboarding.pix_charge.data.entities import PixWebhook
from chatbot.app.onboarding.pix_charge.service import PixChargeResultValidationService
from chatbot.db.postgres import close_session, get_pristine_session
from chatbot.db.postgres.connection import create_thread_safe_context
from chatbot.ext.opentelemetry.helpers import tracing as otel_tracing
from chatbot.workers.data.entities import ProcessPixChargeMessage
from chatbot.workers.dependencies import (
    create_pix_charge_repo,
    create_webhook_delivery_service,
)
from hermes.pubsub.consumer import PubSubConsumer
from opentelemetry import trace  # type: ignore[attr-defined]
from opentelemetry.trace import SpanKind
from sqlalchemy.ext.asyncio import AsyncSession

logger: logging.Logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def get_callback() -> Callable[
    [str, dict[str, str | bytes], ProcessPixChargeMessage],
    Coroutine[Any, Any, None],
]:
    """Get callback function for processing PIX charge messages."""

    async def callback(
        message_id: str,
        attributes: dict[str, str | bytes],
        message: ProcessPixChargeMessage,
    ) -> None:
        with tracer.start_as_current_span(
            "process_pix_charge_webhook",
            otel_tracing.retrieve_propagated_context(
                str(attributes.get("traceparent"))
            ),
            kind=SpanKind.CONSUMER,
            attributes={
                "attribute.message_id": message_id,
                "attribute.qr_code_id": message.message.qr_code_id,
            },
        ) as tracing:
            session: AsyncSession = get_pristine_session()

            try:
                tracing.add_event("Started processing PIX charge webhook")

                repo = create_pix_charge_repo(session)

                webhook_delivery = create_webhook_delivery_service(session)

                webhook_data: (
                    PixWebhook | None
                ) = await PixChargeResultValidationService(
                    repo=repo
                ).validate_pix_event(message=message)

                if webhook_data:
                    await webhook_delivery.notify_pix_accepted(
                        application_id=webhook_data.application_id,
                        chat_id=webhook_data.chat_id,
                        pix_id=webhook_data.pix_id,
                    )

                tracing.add_event("Finished processing PIX charge webhook")

            except Exception as e:
                logger.exception(
                    "Error processing PIX charge webhook (message_id=%s): %s",
                    message_id,
                    e,
                )
                tracing.record_exception(e)
                raise
            finally:
                await close_session(session=session)

    return callback


def process() -> None:
    """Start PIX charge webhook consumer."""
    create_thread_safe_context(is_single_threaded=True)
    consumer = PubSubConsumer(
        project_id=settings.PROJECT_ID,
        subscription_id=settings.PROCESS_PIX_CHARGE_WEBHOOK_SUB_NAME,
        message_model=ProcessPixChargeMessage,
        max_messages=settings.MAX_MESSAGES,
    )
    consumer.run(get_callback())  # type: ignore
