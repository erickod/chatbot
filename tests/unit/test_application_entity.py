from datetime import datetime, timezone
from uuid import uuid7

from chatbot.domain.entities.application import Application, ApplicationStatus
from chatbot.domain.entities.step_execution import StepExecution


def _make_step(*, is_final: bool, status: str) -> StepExecution:
    now = datetime.now(timezone.utc)
    return StepExecution(
        id=uuid7(),
        application_id=uuid7(),
        name="name",
        status=status,
        is_final=is_final,
        created_at=now,
    )


def test_given_application_created_when_check_status_then_is_in_progress_enum() -> None:
    """
    GIVEN a new Application created via Application.create()
    WHEN  the status field is inspected
    THEN  it equals ApplicationStatus.IN_PROGRESS and is of type ApplicationStatus
    """
    app = Application.create(
        originator_phone="111",
        company_phone="222",
    )

    assert app.status == ApplicationStatus.IN_PROGRESS
    assert isinstance(app.status, ApplicationStatus)


def test_given_non_final_step_when_advance_step_then_status_is_in_progress() -> None:
    """
    GIVEN an Application and a non-final step execution
    WHEN  advance_step() is called
    THEN  the application status remains ApplicationStatus.IN_PROGRESS
    """
    app = Application.create(originator_phone="111", company_phone="222")
    step = _make_step(is_final=False, status="COMPLETED")

    app.advance_step(step)

    assert app.status == ApplicationStatus.IN_PROGRESS


def test_given_final_completed_step_when_advance_step_then_status_is_completed() -> (
    None
):
    """
    GIVEN an Application and a final, completed step execution
    WHEN  advance_step() is called
    THEN  the application status is ApplicationStatus.COMPLETED
    """
    app = Application.create(originator_phone="111", company_phone="222")
    step = _make_step(is_final=True, status="COMPLETED")

    app.advance_step(step)

    assert app.status == ApplicationStatus.COMPLETED
