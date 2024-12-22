from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sentry_sdk import capture_exception

from src.services.logger import user_logger
from src.services.oauth2 import AuthPasswordBearer
from .config import auth_config
from ..users.models import User
from .exceptions import (
    UserNotFoundException,
    IncorrectPasswordException,
    JwtEncodeError
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = AuthPasswordBearer(tokenUrl=auth_config.AUTH_TOKEN_URL)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def validate_user_credentials(db_session: Session, username: str, password: str):
    user = db_session.query(User).filter(User.username == username).first()
    if not user:
        user_logger.user_not_found(username)
        raise UserNotFoundException(username)

    if not verify_password(password, user.hashed_password):
        user_logger.user_invalid_password(username)
        raise IncorrectPasswordException(username)
    
    user_logger.validation_success(username)
    return user

def create_access_token(user_data, expires_delta=None):
    to_encode = user_data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=auth_config.DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, auth_config.SECRET_KEY, algorithm=auth_config.ALGORITHM)
    except JWTError as e:
        user_logger.jwt_encode_failed(e)
        capture_exception(e)
        raise JwtEncodeError()

    user_logger.jwt_encode_success()
    return encoded_jwt