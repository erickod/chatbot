from .domain_exception import DomainException


class ValidationError(DomainException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
