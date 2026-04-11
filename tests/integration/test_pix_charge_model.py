from pathlib import Path

from sqlalchemy import BigInteger, String

from chatbot.infra.orm.sqlalchemy.models import DBPixCharge


def test_given_pix_charge_model_when_declared_then_fk_targets_application() -> None:
    """
    GIVEN the DBPixCharge ORM model declaration
    WHEN  the application_id column foreign keys are inspected
    THEN  the foreign key target is application.id without unique constraint
    """
    application_id_column = DBPixCharge.__table__.c.application_id
    foreign_key = next(iter(application_id_column.foreign_keys))

    assert foreign_key.target_fullname == "application.id"
    assert foreign_key.ondelete == "RESTRICT"
    assert application_id_column.unique is not True


def test_given_pix_charge_model_when_declared_then_columns_match_spec() -> None:
    """
    GIVEN the DBPixCharge ORM model declaration
    WHEN  its columns are inspected
    THEN  the table and columns match the approved schema
    """
    table = DBPixCharge.__table__

    assert table.name == "pix_charge"
    assert isinstance(table.c.provider.type, String)
    assert table.c.provider.nullable is False
    assert table.c.provider_id.unique is True
    assert isinstance(table.c.transaction_id.type, String)
    assert isinstance(table.c.amount_cents.type, BigInteger)
    assert table.c.currency.server_default is not None
    assert table.c.currency.server_default.arg == "BRL"
    assert isinstance(table.c.qr_code_text.type, String)
    assert table.c.qr_code_text.nullable is True
    assert isinstance(table.c.qr_code_uri.type, String)
    assert table.c.status.nullable is False
    assert table.c.status.server_default is None
    assert table.c.expires_at.nullable is True
    assert table.c.paid_at.nullable is True
    assert table.c.cancelled_at.nullable is True


def test_given_db_doc_when_updated_then_pix_charge_table_is_documented() -> None:
    """
    GIVEN the database documentation file
    WHEN  its contents are inspected
    THEN  the pix_charge table is documented with key schema details
    """
    db_doc_path = Path(__file__).resolve().parents[2] / ".ai_context" / "DB.md"
    db_doc = db_doc_path.read_text(encoding="utf-8")

    assert "### PIX_CHARGE" in db_doc
    assert "`pix_charge`" in db_doc
    assert "provider_id" in db_doc
    assert "provider" in db_doc
    assert "application.id" in db_doc
    assert "RESTRICT" in db_doc
