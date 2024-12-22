class LLMClientExceptionBase(Exception):
    """Base class for all exceptions in the LLM client module."""
    pass


class InvalidResponseFormatException(LLMClientExceptionBase):
    """Raised when the response format is invalid or unexpected."""
    def __init__(self, message: str = "The AI response format is invalid or unexpected"):
        super().__init__(message)


class LLMRequestFailedException(LLMClientExceptionBase):
    """Raised when the request to the LLM API fails."""
    def __init__(self):
        super().__init__("Failed to generate response from LLM")


class RelevanceLevelException(LLMClientExceptionBase):
    """Raised when the relevance level is unexpected or invalid."""
    def __init__(self):
        super().__init__(f"Unexpected relevance level")
