import pytest

from chatbot.domain.exceptions import ValidationError
from chatbot.domain.value_objects import CNPJNationalID, NationalIDType


def test_given_valid_unmasked_cnpj_when_created_then_value_stored_as_digits():
    """
    GIVEN a valid CNPJ string without mask (digits only)
    WHEN  CNPJNationalID is instantiated
    THEN  value is stored as digits only
    """
    vo = CNPJNationalID(value="11222333000181")
    assert vo.value == "11222333000181"


def test_given_valid_masked_cnpj_when_created_then_value_normalized_to_digits():
    """
    GIVEN a valid CNPJ string with standard mask (XX.XXX.XXX/XXXX-XX)
    WHEN  CNPJNationalID is instantiated
    THEN  value is normalized to digits only (mask removed)
    """
    vo = CNPJNationalID(value="11.222.333/0001-81")
    assert vo.value == "11222333000181"


def test_given_cnpj_national_id_when_type_accessed_then_returns_cnpj():
    """
    GIVEN a valid CNPJNationalID instance
    WHEN  the type attribute is accessed
    THEN  it returns NationalIDType.CNPJ
    """
    vo = CNPJNationalID(value="11222333000181")
    assert vo.type == NationalIDType.CNPJ


def test_given_invalid_check_digits_when_created_then_raises_validation_error():
    """
    GIVEN a 14-digit CNPJ string with incorrect check digits
    WHEN  CNPJNationalID is instantiated
    THEN  a domain ValidationError is raised
    """
    with pytest.raises(ValidationError):
        CNPJNationalID(value="11222333000100")


def test_given_all_same_digits_when_created_then_raises_validation_error():
    """
    GIVEN a CNPJ string where all 14 digits are the same (e.g. 00000000000000)
    WHEN  CNPJNationalID is instantiated
    THEN  a domain ValidationError is raised
    """
    with pytest.raises(ValidationError):
        CNPJNationalID(value="00000000000000")


def test_given_wrong_length_cnpj_when_created_then_raises_validation_error():
    """
    GIVEN a CNPJ string that after normalization has fewer than 14 digits
    WHEN  CNPJNationalID is instantiated
    THEN  a domain ValidationError is raised
    """
    with pytest.raises(ValidationError):
        CNPJNationalID(value="1122233300018")


def test_given_partial_mask_when_created_then_mask_chars_removed():
    """
    GIVEN a valid CNPJ string with partial mask characters (dots, slash, dash)
    WHEN  CNPJNationalID is instantiated
    THEN  all mask characters are removed from value
    """
    vo = CNPJNationalID(value="11.222.333/0001-81")
    assert "." not in vo.value
    assert "/" not in vo.value
    assert "-" not in vo.value
