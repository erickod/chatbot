from chatbot.ext.exceptions import IntegrationError


class IdwallAPIError(IntegrationError):
    """Raised when Idwall API returns an error."""

    def __init__(self, status_code: int, message: str, response_body: str = ""):
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        super().__init__(
            f"Idwall API error {status_code}: {message}"
            + (f" - {response_body[:200]}" if response_body else "")
        )
