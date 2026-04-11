from sqlalchemy import Boolean, Integer, String

from chatbot.infra.orm.sqlalchemy.models import (
    ConsentStatus,
    DBConsent,
    DBTerms,
)


def test_given_db_terms_when_inspected_then_tablename_is_terms() -> None:
    """
    GIVEN the DBTerms ORM model declaration
    WHEN  its table metadata is inspected
    THEN  the table name is terms
    """
    assert DBTerms.__table__.name == "terms"


def test_given_db_terms_when_inspected_then_version_is_integer_and_unique() -> None:
    """
    GIVEN the DBTerms ORM model declaration
    WHEN  the version column metadata is inspected
    THEN  it is a required Integer column with unique constraint
    """
    col = DBTerms.__table__.c.version

    assert isinstance(col.type, Integer)
    assert col.nullable is False
    assert col.unique is True


def test_given_db_terms_when_inspected_then_link_is_string_not_nullable() -> None:
    """
    GIVEN the DBTerms ORM model declaration
    WHEN  the link column metadata is inspected
    THEN  it is a required String column
    """
    col = DBTerms.__table__.c.link

    assert isinstance(col.type, String)
    assert col.nullable is False


def test_given_db_terms_when_inspected_then_is_active_has_true_server_default() -> None:
    """
    GIVEN the DBTerms ORM model declaration
    WHEN  the is_active column metadata is inspected
    THEN  it is a required Boolean column with server_default true
    """
    col = DBTerms.__table__.c.is_active

    assert isinstance(col.type, Boolean)
    assert col.nullable is False
    assert col.server_default is not None
    assert col.server_default.arg == "true"


def test_given_db_consent_when_inspected_then_tablename_is_application_consent() -> (
    None
):
    """
    GIVEN the DBConsent ORM model declaration
    WHEN  its table metadata is inspected
    THEN  the table name is application_consent
    """
    assert DBConsent.__table__.name == "application_consent"


def test_given_db_consent_when_inspected_then_application_id_has_cascade_fk() -> None:
    """
    GIVEN the DBConsent ORM model declaration
    WHEN  the application_id column foreign keys are inspected
    THEN  the foreign key targets application.id with CASCADE and is not nullable
    """
    col = DBConsent.__table__.c.application_id
    fk = next(iter(col.foreign_keys))

    assert fk.target_fullname == "application.id"
    assert fk.ondelete == "CASCADE"
    assert col.nullable is False


def test_given_db_consent_when_inspected_then_terms_id_has_restrict_fk() -> None:
    """
    GIVEN the DBConsent ORM model declaration
    WHEN  the terms_id column foreign keys are inspected
    THEN  the foreign key targets terms.id with RESTRICT and is not nullable
    """
    col = DBConsent.__table__.c.terms_id
    fk = next(iter(col.foreign_keys))

    assert fk.target_fullname == "terms.id"
    assert fk.ondelete == "RESTRICT"
    assert col.nullable is False


def test_given_db_consent_when_inspected_then_status_has_pending_server_default() -> (
    None
):
    """
    GIVEN the DBConsent ORM model declaration
    WHEN  the status column metadata is inspected
    THEN  it is a required String column with server_default PENDING
    """
    col = DBConsent.__table__.c.status

    assert isinstance(col.type, String)
    assert col.nullable is False
    assert col.server_default is not None
    assert col.server_default.arg == "PENDING"


def test_given_consent_status_when_checked_then_has_pending_blocked_completed() -> None:
    """
    GIVEN the ConsentStatus enum
    WHEN  its values are listed
    THEN  they match PENDING, BLOCKED, COMPLETED exactly
    """
    assert [s.value for s in ConsentStatus] == ["PENDING", "BLOCKED", "COMPLETED"]
