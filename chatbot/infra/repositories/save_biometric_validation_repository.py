from chatbot.domain.entities.biometric_validation import BiometricValidation
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import DBBiometricValidation, DBStepExecution


class SABiometricValidationRepository(BaseRepository):
    async def create(self, biometric: BiometricValidation) -> None:
        step = biometric.step_execution
        self.db_session.add(
            DBBiometricValidation(
                id=biometric.id,
                application_id=biometric.application_id,
                provider_id=biometric.provider_id,
                status=biometric.status.value,
                validation_result=biometric.validation_result,
            )
        )
        self.db_session.add(
            DBStepExecution(
                id=step.id,
                application_id=step.application_id,
                name=step.name,
                status=str(step.status),
                data={
                    "provider_id": biometric.provider_id,
                    "validation_result": biometric.validation_result,
                },
            )
        )
