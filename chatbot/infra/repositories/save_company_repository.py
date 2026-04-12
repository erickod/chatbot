from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from chatbot.domain.entities.customer import Customer
from chatbot.domain.value_objects.cnpj_national_id import CNPJNationalID
from chatbot.infra.db.postgres.base_repository import BaseRepository
from chatbot.infra.orm.sqlalchemy.models import (
    DBApplication,
    DBCustomer,
    DBStepExecution,
)


class SACompanyRepository(BaseRepository):
    async def create(self, customer: Customer) -> None:
        step = customer.step_execution
        stmt = insert(DBCustomer).values(
            id=customer.id,
            application_id=customer.application_id,
            national_id=customer.national_id.value,
            trading_name=customer.trading_name,
            status=customer.status,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
        await self.db_session.execute(stmt)
        self.db_session.add(
            DBStepExecution(
                id=step.id,
                application_id=step.application_id,
                name=step.name,
                status=str(step.status),
                data=customer.model_dump(mode="json"),
                created_at=customer.created_at,
                updated_at=customer.updated_at,
            )
        )
        await self.db_session.commit()

    async def load_by_phones(
        self, originator_phone: str, company_phone: str
    ) -> Customer | None:
        stmt = (
            select(DBCustomer)
            .join(DBApplication, DBApplication.id == DBCustomer.application_id)
            .where(
                DBApplication.originator_phone == originator_phone,
                DBApplication.company_phone == company_phone,
            )
        )
        if row := (await self.db_session.execute(stmt)).scalar_one_or_none():
            customer = Customer(
                id=row.id,
                application_id=row.application_id,
                national_id=CNPJNationalID(row.national_id),
                trading_name=row.trading_name,
                status=row.status,
                created_at=row.created_at,
                updated_at=row.updated_at or row.created_at,
            )
            return customer
