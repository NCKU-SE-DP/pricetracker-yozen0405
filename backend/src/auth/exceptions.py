class AuthenticationExceptionBase(Exception):
    def __init__(self, message="Authentication exception occurred"):
        self.message = message
        super().__init__(self.message)
        
class UserNotFoundException(AuthenticationExceptionBase):
     def __init__(self, username: str):
        super().__init__(f"User '{username}' not found")

class IncorrectPasswordException(AuthenticationExceptionBase):
     def __init__(self, username: str):
        super().__init__(f"Incorrect password for user '{username}'")

class JwtEncodeError(AuthenticationExceptionBase):
    pass