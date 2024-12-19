from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from typing import Optional
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request
from src.services.logger import user_logger
from src.services.exceptions_handler import UnauthorizedException

class AuthPasswordBearer(OAuth2PasswordBearer):
    """
    自定義 OAuth2 Bearer Token 的依賴函數，用於處理未提供 Token 的情況並記錄日誌。
    """

    def __init__(self, tokenUrl: str, **kwargs):
        super().__init__(tokenUrl=tokenUrl)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            user_logger.missing_authenticate_token()
            raise UnauthorizedException()

        return param