from fastapi import Depends
from jose import jwt

from .database import engine, SessionLocal
from .auth.config import auth_config
from .users.models import User
from .auth.service import oauth2_scheme

def session_opener():
    session = SessionLocal(bind=engine)
    try:
        yield session
    finally:
        session.close()

def get_current_user(
    token = Depends(oauth2_scheme),
    db = Depends(session_opener)
):
    payload = jwt.decode(token, auth_config.SECRET_KEY, algorithms=auth_config.ALGORITHM)
    return db.query(User).filter(User.username == payload.get("sub")).first()