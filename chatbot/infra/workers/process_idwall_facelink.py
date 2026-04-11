import logging
from typing import Any, Callable, Coroutine

# TODO: this came from another project e must be adapted use BiometricValidation entity
import settings
from chatbot.app.onboarding.biometric.data.entitites import BiometricWebhook
from chatbot.db.postgres import close_session, get_pristine_session
from chatbot.db.postgres.connection import create_thread_safe_context
from chatbot.ext.opentelemetry.helpers import tracing as otel_tracing
from chatbot.workers.data.entities import ProcessBiometricValidationMessage
from chatbot.workers.dependencies import (
    create_biometric_service,
    create_webhook_delivery_service,
)
from hermes.pubsub.consumer import PubSubConsumer
from opentelemetry import trace  # type: ignore[attr-defined]
from opentelemetry.trace import SpanKind, StatusCode
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def get_callback() -> Callable[
    [str, dict[str, str | bytes], ProcessBiometricValidationMessage],
    Coroutine[Any, Any, None],
]:
    """Get callback function for processing biometric validation messages."""

    async def callback(
        message_id: str,
        attributes: dict[str, str | bytes],
        message: ProcessBiometricValidationMessage,
    ) -> None:
        with tracer.start_as_current_span(
            "process_facelink_webhook",
            otel_tracing.retrieve_propagated_context(
                str(attributes.get("traceparent"))
            ),
            kind=SpanKind.CONSUMER,
            attributes={
                "attribute.message_id": message_id,
                "attribute.registration_id": message.message.registration_id,
            },
        ) as tracing:
            create_thread_safe_context()

            session: AsyncSession = get_pristine_session()

            try:
                tracing.add_event("Started processing biometric validation")

                biometric_service = create_biometric_service(session)

                webhook_data: BiometricWebhook = (
                    await biometric_service.process_biometric_result(message)
                )

                webhook_service = create_webhook_delivery_service(session)

                if webhook_data.was_approved:
                    await webhook_service.notify_idwall_accepted(
                        application_id=webhook_data.application_id,
                        chat_id=webhook_data.chat_id,
                    )
                else:
                    await webhook_service.notify_idwall_not_accepted(
                        application_id=webhook_data.application_id,
                        chat_id=webhook_data.chat_id,
                    )

                tracing.add_event(
                    "Finished processing biometric validation",
                    attributes={
                        "attribute.biometric_rwas_approved": webhook_data.was_approved,
                    },
                )
            except Exception as e:
                tracing.add_event("Error processing biometric result")
                tracing.set_status(StatusCode.ERROR)
                tracing.record_exception(e)
                raise
            finally:
                await close_session(session=session)

    return callback


def process() -> None:
    consumer = PubSubConsumer(
        project_id=settings.PROJECT_ID,
        subscription_id=settings.PROCESS_FACELINK_WEBHOOK_SUB_NAME,
        message_model=ProcessBiometricValidationMessage,
        max_messages=settings.MAX_MESSAGES,
    )
    consumer.run(get_callback())  # type: ignore
