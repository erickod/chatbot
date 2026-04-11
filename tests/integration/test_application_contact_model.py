from chatbot.infra.orm.sqlalchemy.models import DBOnboardingApplicationContact


def test_given_application_contact_model_when_declared_then_fk_targets_application() -> (
    None
):
    """
    GIVEN the DBOnboardingApplicationContact ORM model declaration
    WHEN  the application_id column foreign keys are inspected
    THEN  the foreign key target is application.id
    """
    application_id_column = DBOnboardingApplicationContact.__table__.c.application_id
    foreign_key = next(iter(application_id_column.foreign_keys))

    assert foreign_key.target_fullname == "application.id"
    assert foreign_key.ondelete == "CASCADE"
    assert application_id_column.unique is True


def test_given_application_contact_model_when_declared_then_nullable_columns_match_spec() -> (
    None
):
    """
    GIVEN the DBOnboardingApplicationContact ORM model declaration
    WHEN  its columns are inspected
    THEN  cpf, name, email and role are nullable and table name matches spec
    """
    table = DBOnboardingApplicationContact.__table__

    assert table.name == "application_contact"
    assert table.c.cpf.nullable is True
    assert table.c.name.nullable is True
    assert table.c.email.nullable is True
    assert table.c.role.nullable is True
