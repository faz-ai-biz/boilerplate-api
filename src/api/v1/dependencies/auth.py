from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import InvalidTokenError
from src.core.token_manager import decode_token
from src.db.session import get_db
from src.utils.logging import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate access token and return current user."""
    try:
        logger.debug("Validating access token in get_current_user dependency")
        payload = decode_token(token, token_type=settings.TOKEN_TYPE_ACCESS)
        user_id = payload.get("user_id")
        if not user_id:
            logger.error("No user_id found in token payload")
            raise InvalidTokenError("Invalid token: no user_id")

        logger.debug(f"Token validated successfully for user_id: {user_id}")
        return {"id": user_id}

    except InvalidTokenError as exc:
        logger.info(f"Token validation failed: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )
