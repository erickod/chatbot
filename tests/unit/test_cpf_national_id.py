import pytest

from chatbot.domain.exceptions import ValidationError
from chatbot.domain.value_objects import CPFNationalID, NationalIDType


def test_given_masked_cpf_when_instantiated_then_returns_normalized_value():
    """
    GIVEN a valid CPF string with mask
    WHEN  CPFNationalID is instantiated
    THEN  it stores only the normalized digits
    """
    vo = CPFNationalID(value="529.982.247-25")

    assert vo.value == "52998224725"


def test_given_unmasked_cpf_when_instantiated_then_keeps_normalized_value():
    """
    GIVEN a valid CPF string without mask
    WHEN  CPFNationalID is instantiated
    THEN  it keeps the normalized digits unchanged
    """
    vo = CPFNationalID(value="52998224725")

    assert vo.value == "52998224725"


def test_given_invalid_cpf_when_instantiated_then_raises_validation_error():
    """
    GIVEN a CPF string with invalid check digits
    WHEN  CPFNationalID is instantiated
    THEN  a ValidationError is raised
    """
    with pytest.raises(ValidationError):
        CPFNationalID(value="52998224724")


def test_given_short_cpf_when_instantiated_then_raises_validation_error():
    """
    GIVEN a CPF string shorter than 11 digits
    WHEN  CPFNationalID is instantiated
    THEN  a ValidationError is raised
    """
    with pytest.raises(ValidationError):
        CPFNationalID(value="5299822472")


def test_given_national_id_type_when_accessed_then_exposes_cpf_and_cnpj():
    """
    GIVEN the NationalIDType enum
    WHEN  its CPF and CNPJ members are accessed
    THEN  both national id types are available
    """
    assert NationalIDType.CPF.value == "CPF"
    assert NationalIDType.CNPJ.value == "CNPJ"
