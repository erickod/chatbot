from uuid import UUID

from chatbot.domain.entities import OriginatorSeller, OriginatorSellerStatus


def test_given_originator_seller_when_created_then_attaches_seller_step() -> None:
    """
    GIVEN valid originator seller arguments
    WHEN  OriginatorSeller.create() is called
    THEN  it attaches a seller step execution with matching ids
    """
    seller = OriginatorSeller.create(
        application_id=UUID(int=1),
        name="Jane Doe",
        email="jane@example.com",
        position="owner",
    )

    assert seller.step_execution is not None
    assert seller.step_execution.id == seller.id
    assert seller.step_execution.application_id == seller.application_id
    assert seller.step_execution.name == "seller"


def test_given_originator_seller_when_created_then_status_is_completed() -> None:
    """
    GIVEN valid originator seller arguments
    WHEN  OriginatorSeller.create() is called
    THEN  the returned instance has status COMPLETED
    """
    seller = OriginatorSeller.create(
        application_id=UUID(int=1),
        name="Jane Doe",
        email="jane@example.com",
        position="owner",
    )

    assert seller.status == OriginatorSellerStatus.COMPLETED


def test_given_originator_seller_when_created_then_step_data_is_complete() -> None:
    """
    GIVEN valid originator seller arguments
    WHEN  OriginatorSeller.create() is called
    THEN  step execution data contains normalized seller fields
    """
    seller = OriginatorSeller.create(
        application_id=UUID(int=1),
        name="Jane Doe",
        email="jane@example.com",
        position="owner",
    )

    assert seller.step_execution is not None
    assert seller.step_execution.data == {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "position": "owner",
    }


def test_given_entities_package_when_importing_then_seller_symbols_are_exported() -> (
    None
):
    """
    GIVEN the chatbot.domain.entities package
    WHEN  OriginatorSeller and OriginatorSellerStatus are imported from it
    THEN  both symbols are exported and usable
    """
    assert OriginatorSeller.__name__ == "OriginatorSeller"
    assert OriginatorSellerStatus.COMPLETED == "COMPLETED"
