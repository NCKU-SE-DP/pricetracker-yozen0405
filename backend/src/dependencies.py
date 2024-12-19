from fastapi import Depends
from jose import jwt, JWTError, ExpiredSignatureError

from .database import engine, SessionLocal
from .auth.config import auth_config
from .users.models import User
from .auth.service import oauth2_scheme
from src.services.logger import user_logger
from src.services.exceptions_handler import (
    TokenExpiredException,
    InvalidTokenException,
    MissingSubTokenException
)

def session_opener():
    session = SessionLocal(bind=engine)
    try:
        yield session
    finally:
        session.close()

def get_current_user(
    token=Depends(oauth2_scheme),
    db=Depends(session_opener)
):
    try:
        payload = jwt.decode(token, auth_config.SECRET_KEY, algorithms=[auth_config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            user_logger.missing_sub_field_in_token(token)
            raise MissingSubTokenException()

    except ExpiredSignatureError:
        user_logger.token_expired(token)
        raise TokenExpiredException()

    except JWTError as e:
        user_logger.invalid_jwt_token(token=token, error=e)
        raise InvalidTokenException()

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        user_logger.invalid_jwt_token(token=token)
        raise InvalidTokenException()
    user_logger.user_authenticated_success(username)

    return user