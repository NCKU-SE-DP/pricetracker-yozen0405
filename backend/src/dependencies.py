from fastapi import Depends, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from sentry_sdk import capture_exception
import logging

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
    token=Depends(oauth2_scheme),
    db=Depends(session_opener)
):
    try:
        payload = jwt.decode(token, auth_config.SECRET_KEY, algorithms=[auth_config.ALGORITHM])
    except ExpiredSignatureError:
        logging.debug("Authentication token has expired")
        raise HTTPException(status_code=401, detail="Authentication token has expired")
    except JWTError as e:
        logging.debug("Invalid jwt authentication token")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except Exception as e:
        capture_exception(e)
        logging.warning(f"Failed to decode token: {token}, error: {e}")
        raise HTTPException(status_code=500, detail="Unexcepted error occured.")
    
    username: str = payload.get("sub")
    if username is None:
        logging.debug("Missing sub field in token")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logging.debug("User in jwt token doesnt exist")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    logging.debug("Authentication token verified")
    return user