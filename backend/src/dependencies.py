from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError

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
    try:
        payload = jwt.decode(token, auth_config.SECRET_KEY, algorithms=[auth_config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token: missing 'sub' field",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:   
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user