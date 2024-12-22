from datetime import timedelta
from sentry_sdk import capture_exception
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.services.logger import user_logger
from src.auth.exceptions import (
    UserNotFoundException,
    IncorrectPasswordException,
    JwtEncodeError
)
from ..dependencies import session_opener, get_current_user
from .schemas import UserAuthSchema
from .models import User
from .config import user_config
from ..auth.constant import MAX_PASSWORD_SIZE, MAX_USERNAME_SIZE
from ..auth.service import (
    validate_user_credentials,
    create_access_token,
    pwd_context
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(session_opener)
):
    """
    Authenticates a user and generates an access token.

    :param form_data: Form data containing username and password.
    :param db: Database session dependency.
    :return: JSON with access token and token type.
    """
    try:
        user = validate_user_credentials(db, form_data.username, form_data.password)
    except (UserNotFoundException, IncorrectPasswordException) as e:
        user_logger.user_login_failed(form_data.username)
        raise HTTPException(status_code=400, detail=e.message)

    try:
        access_token = create_access_token(
            user_data={"sub": str(user.username)},
            expires_delta=timedelta(minutes=user_config.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
    except JwtEncodeError as e:
        capture_exception(e)
        user_logger.user_login_failed(form_data.username)
        raise HTTPException(status_code=500, detail="Unxcepted error occured, please tried again.")

    user_logger.user_login(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
def create_user(user: UserAuthSchema, db: Session = Depends(session_opener)):
    """
    Registers a new user with a hashed password.

    :param user: User data containing username and password.
    :param db: Database session dependency.
    :return: The created user object.
    """
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        user_logger.user_already_exists(username=user.username)
        raise HTTPException(status_code=400, detail=f"User '{user.username}' already exists")
    
    if len(user.username) > MAX_USERNAME_SIZE:
        user_logger.username_too_long(username=user.username)
        raise HTTPException(status_code=400, detail=f"Username too long (maximum {MAX_USERNAME_SIZE} characters)")
    
    if len(user.password) > MAX_PASSWORD_SIZE:
        user_logger.password_too_long(username=user.username)
        raise HTTPException(status_code=400, detail=f"Password too long (maximum {MAX_PASSWORD_SIZE} characters)")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        capture_exception(e)
        user_logger.user_registration_error(username=user.username, error=e)
        raise HTTPException(status_code=500, detail=f"An unexcepted error occured, failed to register.")

@router.get("/me")
def read_users_me(user=Depends(get_current_user)):
    return {"username": user.username}