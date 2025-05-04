from typing import Optional

class TokenExceededError(ValueError):
    def __init__(self, kind: str, limit: int, actual: int) -> None:
        message = f"{kind.capitalize()} limit exceeded: allowed {limit}, got {actual}."
        super().__init__(message)
        self.kind = kind
        self.limit = limit
        self.actual = actual

class EmptyContentError(ValueError):
    """Exception raised when the ChatCompletion response has no content."""

    def __init__(self, response_raw: object) -> None:
        self.response_raw = response_raw
        message = "The ChatCompletion response contained no content."
        super().__init__(message)

class OutputParsingError(Exception):
    """Raised when an LLM output cannot be parsed into the expected format."""

    def __init__(self, message: str = "Failed to parse the LLM response output.", response: Optional[str] = None):
        self.message = message
        self.response = response
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        if self.response:
            return f"{self.message}\nResponse:\n{self.response}"
        return self.message