from enum import Enum


class NationalIDType(str, Enum):
    CNPJ = "CNPJ"
    CPF = "CPF"
