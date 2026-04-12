from typing import Any, Callable, Coroutine

from hermes.pubsub.consumer import PubSubConsumer
from hermes.pubsub.consumer.base import BaseModel
from settings import settings

from chatbot.infra.db.postgres import create_thread_safe_context


class ProcessBiometricValidationMessage(BaseModel): ...


def get_callback() -> Callable[
    [str, dict[str, str | bytes], ProcessBiometricValidationMessage],
    Coroutine[Any, Any, None],
]: ...


def process() -> None:
    create_thread_safe_context(is_single_threaded=True)
    consumer = PubSubConsumer(
        project_id=settings.PROJECT_ID,
        subscription_id=settings.PROCESS_FACELINK_WEBHOOK_SUB_NAME,
        message_model=ProcessBiometricValidationMessage,
        max_messages=settings.MAX_MESSAGES,
    )
    consumer.run(get_callback())  # type: ignore
