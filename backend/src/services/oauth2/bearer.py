from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request
from src.services.logger import user_logger
from src.auth.exceptions import UnauthorizedException

class AuthPasswordBearer(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str, **kwargs):
        super().__init__(tokenUrl=tokenUrl)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            user_logger.missing_authenticate_token()
            raise UnauthorizedException()

        return param