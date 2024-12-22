class CrawlerExceptionsBase(Exception):
    """Base class for all exceptions in the crawler module."""
    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        super().__init__(message, *args, **kwargs)


class DomainMismatchException(CrawlerExceptionsBase):
    """Raised when the URL domain does not match the expected domain."""
    def __init__(self, url: str):
        message = f"Domain mismatch for URL: {url}"
        super().__init__(message)


class InvalidResponseException(CrawlerExceptionsBase):
    """Raised when the response is invalid or cannot be processed."""
    def __init__(self):
        message = f"Invalid response received"
        super().__init__(message)

class InvalidHeadlineExceptions(CrawlerExceptionsBase):
    def __init__(self):
        message = f"Invalid headline to parsse"
        super().__init__(message)

class SavingExistingNewsException(CrawlerExceptionsBase):
    def __init__(self, url: str):
        message = f"Saving existing news. URL: {url}"
        super().__init__(message)

class ParsingException(CrawlerExceptionsBase):
    """Raised when there is an error during parsing."""
    def __init__(self):
        message = f"Failed to parse content."
        super().__init__(message)

class ExtractNewsException(CrawlerExceptionsBase):
    def __init__(self):
        message = f"Failed to extract news."
        super().__init__(message)

class DatabaseSaveException(CrawlerExceptionsBase):
    """Raised when saving to the database fails."""
    def __init__(self):
        message = f"Failed to save news to database."
        super().__init__(message)