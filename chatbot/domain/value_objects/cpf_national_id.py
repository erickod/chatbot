from dataclasses import dataclass

from chatbot.domain.exceptions import ValidationError
from chatbot.domain.value_objects.national_id_type import NationalIDType


@dataclass(frozen=True)
class CPFNationalID:
    value: str
    type: NationalIDType = NationalIDType.CPF

    def __post_init__(self) -> None:
        normalized = self.value.replace(".", "").replace("-", "")
        object.__setattr__(self, "value", normalized)
        self._validate(normalized)

    @staticmethod
    def _validate(digits: str) -> None:
        if len(digits) != 11:
            raise ValidationError("CPF must have 11 digits")
        if len(set(digits)) == 1:
            raise ValidationError("CPF cannot have all identical digits")

        first_weights = range(10, 1, -1)
        remainder = (
            sum(int(digit) * weight for digit, weight in zip(digits[:9], first_weights))
            % 11
        )
        check_1 = 0 if remainder < 2 else 11 - remainder

        second_weights = range(11, 1, -1)
        remainder = (
            sum(
                int(digit) * weight
                for digit, weight in zip(digits[:10], second_weights)
            )
            % 11
        )
        check_2 = 0 if remainder < 2 else 11 - remainder

        if int(digits[9]) != check_1 or int(digits[10]) != check_2:
            raise ValidationError("CPF has invalid check digits")
