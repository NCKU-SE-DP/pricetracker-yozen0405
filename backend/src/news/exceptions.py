class NewsExceptionBase(Exception):
    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        super().__init__(message, *args, **kwargs)


class NewsDoesntExistException(NewsExceptionBase):
    def __init__(self):
        message = f"News doesn't exitst."
        super().__init__(message)