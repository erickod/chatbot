from dataclasses import dataclass

from chatbot.domain.exceptions import ValidationError
from chatbot.domain.value_objects.national_id_type import NationalIDType


@dataclass(frozen=True)
class CNPJNationalID:
    value: str
    type: NationalIDType = NationalIDType.CNPJ

    def __post_init__(self) -> None:
        normalized = self.value.replace(".", "").replace("/", "").replace("-", "")
        object.__setattr__(self, "value", normalized)
        self._validate(normalized)

    @staticmethod
    def _validate(digits: str) -> None:
        if len(digits) != 14:
            raise ValidationError("CNPJ must have 14 digits")
        if len(set(digits)) == 1:
            raise ValidationError("CNPJ cannot have all identical digits")

        weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        remainder = (
            sum(int(digit) * weight for digit, weight in zip(digits[:12], weights_1))
            % 11
        )
        check_1 = 0 if remainder < 2 else 11 - remainder

        weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        remainder = (
            sum(int(digit) * weight for digit, weight in zip(digits[:13], weights_2))
            % 11
        )
        check_2 = 0 if remainder < 2 else 11 - remainder

        if int(digits[12]) != check_1 or int(digits[13]) != check_2:
            raise ValidationError("CNPJ has invalid check digits")
