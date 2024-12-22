from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request, HTTPException
import logging

class AuthPasswordBearer(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str, **kwargs):
        super().__init__(tokenUrl=tokenUrl)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            logging.debug("User didn't provide authorization token")
            raise HTTPException(status_code=401, detail="Please provide authorization token")

        return param