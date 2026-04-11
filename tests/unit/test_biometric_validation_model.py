from pathlib import Path

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB

from chatbot.infra.orm.sqlalchemy.models import (
    BiometricValidationStatus,
    DBBiometricValidation,
)


def test_given_biometric_validation_status_when_listed_then_values_match_task() -> None:
    """
    GIVEN the BiometricValidationStatus enum
    WHEN  its values are listed
    THEN  they match the statuses approved in the task
    """
    assert [status.value for status in BiometricValidationStatus] == [
        "AWAIT_CONFIRMATION",
        "PENDING",
        "COMPLETED",
        "BLOCKED",
    ]


def test_given_db_biometric_validation_when_inspecting_table_then_name_is_expected() -> (
    None
):
    """
    GIVEN the DBBiometricValidation ORM model declaration
    WHEN  its table metadata is inspected
    THEN  the table name is biometric_validation
    """
    assert DBBiometricValidation.__table__.name == "biometric_validation"


def test_given_application_id_column_when_inspecting_fk_then_targets_application_with_restrict() -> (
    None
):
    """
    GIVEN the DBBiometricValidation ORM model declaration
    WHEN  the application_id column foreign keys are inspected
    THEN  the foreign key target is application.id with RESTRICT
    """
    application_id_column = DBBiometricValidation.__table__.c.application_id
    foreign_key = next(iter(application_id_column.foreign_keys))

    assert foreign_key.target_fullname == "application.id"
    assert foreign_key.ondelete == "RESTRICT"
    assert application_id_column.nullable is False


def test_given_profile_ref_column_when_inspecting_mapping_then_is_string_required_and_indexed() -> (
    None
):
    """
    GIVEN the DBBiometricValidation ORM model declaration
    WHEN  the profile_ref column metadata is inspected
    THEN  it is a required indexed String column
    """
    table = DBBiometricValidation.__table__

    assert isinstance(table.c.profile_ref.type, String)
    assert table.c.profile_ref.nullable is False
    assert table.c.profile_ref.index is True


def test_given_status_column_when_inspecting_mapping_then_is_string_indexed_with_default() -> (
    None
):
    """
    GIVEN the DBBiometricValidation ORM model declaration
    WHEN  the status column metadata is inspected
    THEN  it is a required indexed String column with the approved default
    """
    table = DBBiometricValidation.__table__

    assert isinstance(table.c.status.type, String)
    assert table.c.status.nullable is False
    assert table.c.status.index is True
    assert table.c.status.server_default is not None
    assert table.c.status.server_default.arg == "AWAIT_CONFIRMATION"


def test_given_validation_result_column_when_inspecting_mapping_then_is_required_jsonb() -> (
    None
):
    """
    GIVEN the DBBiometricValidation ORM model declaration
    WHEN  the validation_result column metadata is inspected
    THEN  it is a required JSONB column
    """
    table = DBBiometricValidation.__table__

    assert isinstance(table.c.validation_result.type, JSONB)
    assert table.c.validation_result.nullable is False


def test_given_db_biometric_validation_when_inspecting_constraints_then_has_no_uniqueness() -> (
    None
):
    """
    GIVEN the DBBiometricValidation ORM model declaration
    WHEN  its constraints are inspected
    THEN  there is no uniqueness on application_id or application_id plus profile_ref
    """
    table = DBBiometricValidation.__table__

    assert table.c.application_id.unique is not True
    unique_constraints = [
        tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]

    assert ("application_id",) not in unique_constraints
    assert ("application_id", "profile_ref") not in unique_constraints


def test_given_db_documentation_when_reading_biometric_validation_section_then_matches_model() -> (
    None
):
    """
    GIVEN the database documentation file
    WHEN  its biometric_validation section is inspected
    THEN  it matches the approved model schema
    """
    db_doc_path = Path(__file__).resolve().parents[2] / ".ai_context" / "DB.md"
    db_doc = db_doc_path.read_text(encoding="utf-8")

    assert "### BIOMETRIC_VALIDATION" in db_doc
    assert "`biometric_validation`" in db_doc
    assert "application.id" in db_doc
    assert "AWAIT_CONFIRMATION" in db_doc
    assert "profile_ref" in db_doc
    assert "validation_result" in db_doc
