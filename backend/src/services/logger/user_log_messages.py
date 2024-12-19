from .logger_service import LoggerService, LogMessageInterface
from jose import JWTError
from typing import Optional

class UserLogMessages:
    def __init__(self):
        self.logger = LoggerService("users_service")

    def user_login(self, username: str):
        message = LogMessageInterface(message="User login successful!", username=username)
        self.logger.log_info(message)

    def user_login_failed(self, username: str):
        message = LogMessageInterface(message="User login failed", username=username)
        self.logger.log_info(message)

    def jwt_encode_failed(self, error: JWTError):
        message = LogMessageInterface(message="Jwt encode failed", error=str(error))
        self.logger.log_error(message)

    def jwt_encode_success(self):
        message = LogMessageInterface(message="Jwt encoded successfully")
        self.logger.log_debug(message)

    def user_not_found(self, username: str):
        message = LogMessageInterface(message="User not found during validation", username=username)
        self.logger.log_warning(message)

    def user_invalid_password(self, username: str):
        message = LogMessageInterface(message="Password verification failed", username=username)
        self.logger.log_warning(message)

    def validation_success(self, username: str):
        message = LogMessageInterface(message="User credentials validated successfully", username=username)
        self.logger.log_debug(message)

    def username_too_long(self, username: str):
        message = LogMessageInterface(message="Username too long", username=username)
        self.logger.log_warning(message)

    def password_too_long(self, username: str):
        message = LogMessageInterface(message="Password too long", username=username)
        self.logger.log_warning(message)

    def user_already_exists(self, username: str):
        message = LogMessageInterface(message="User already exists", username=username)
        self.logger.log_warning(message)

    def user_registration(self, username: str):
        message = LogMessageInterface(message="User registered successfully!", username=username)
        self.logger.log_info(message)

    def user_registration_failed(self, username: str):
        message = LogMessageInterface(message="User registration failed", username=username)
        self.logger.log_info(message)

    def user_registration_error(self, username: str, error: Exception):
        message = LogMessageInterface(message="User registration failed", username=username, error=str(error))
        self.logger.log_error(message)

    def jwt_decoded_success(self, username: str):
        message = LogMessageInterface(message="JWT decoded successfully", username=username)
        self.logger.log_debug(message)

    def missing_authenticate_token(self):
        message = LogMessageInterface(message="User missing authenticate token")
        self.logger.log_info(message)

    def missing_sub_field_in_token(self, token: str):
        message = LogMessageInterface(message="Missing 'sub' field in token", token=token)
        self.logger.log_warning(message)

    def token_expired(self, token: str):
        message = LogMessageInterface(message="Token expired", token=token)
        self.logger.log_warning(message)

    def invalid_jwt_token(self, error: Optional[JWTError], token: str):
        error_message = str(error) if error else "No specific error provided"
        message = LogMessageInterface(message="Invalid JWT token", error=error_message, token=token)
        self.logger.log_warning(message)

    def user_authenticated_success(self, username: str):
        message = LogMessageInterface(message="User authentication succeeded", username=username)
        self.logger.log_info(message)

user_logger = UserLogMessages()
