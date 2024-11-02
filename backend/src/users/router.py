from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import session_opener
from .schemas import UserAuthSchema
from ..auth.models import User
from ..auth.service import (
    validate_user_credentials,
    create_access_token,
    pwd_context,
    authenticate_user_token
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
    user = validate_user_credentials(db, form_data.username, form_data.password)
    access_token = create_access_token(
        user_data={"sub": str(user.username)}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
def create_user(user: UserAuthSchema, db: Session = Depends(session_opener)):
    """
    Registers a new user with a hashed password.

    :param user: User data containing username and password.
    :param db: Database session dependency.
    :return: The created user object.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me")
def read_users_me(user=Depends(authenticate_user_token)):
    return {"username": user.username}