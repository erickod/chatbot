from chatbot.domain.entities.payment import Payment
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBPixCharge, DBStepExecution


class SAPaymentRepository(BaseRepository):
    async def create(self, payment: Payment) -> None:
        step = payment.step_execution
        self.db_session.add(
            DBPixCharge(
                id=payment.id,
                application_id=payment.application_id,
                provider=payment.provider,
                provider_id=payment.provider_id,
                transaction_id=payment.transaction_id,
                amount_cents=payment.amount_cents,
                currency=payment.currency,
                qr_code_text=payment.qr_code_text,
                qr_code_uri=payment.qr_code_uri,
                status=payment.status.value,
                expires_at=payment.expires_at,
                paid_at=payment.paid_at,
                cancelled_at=payment.cancelled_at,
            )
        )
        self.db_session.add(
            DBStepExecution(
                id=step.id,
                application_id=step.application_id,
                name=step.name,
                status=str(step.status),
                data={
                    "provider": payment.provider,
                    "provider_id": payment.provider_id,
                    "amount_cents": payment.amount_cents,
                    "status": payment.status.value,
                },
            )
        )
