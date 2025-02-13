import uuid
from datetime import datetime, timedelta
from typing import Dict, Set

import jwt

from src.core.config import settings
from src.core.exceptions import InvalidTokenError
from src.utils.logging import logger

# Token blacklist storage (use Redis in production)
_token_blacklist: Set[str] = set()


def create_access_token(data: Dict, refresh_jti: str = None) -> tuple[str, str]:
    """Create a new access token and return the token along with its JTI."""
    jti = str(uuid.uuid4())
    to_encode = data.copy()
    audience = (
        "test-audience" if settings.ENVIRONMENT == "test" else settings.TOKEN_AUDIENCE
    )

    to_encode.update(
        {
            "jti": jti,
            "refresh_jti": refresh_jti,
            "type": "access",
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "iss": settings.TOKEN_ISSUER,
            "aud": audience,
        }
    )
    encoded_token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_token, jti


def create_refresh_token(data: Dict, access_jti: str = None) -> str:
    """Create a new refresh token with linked access token JTI."""
    jti = str(uuid.uuid4())
    to_encode = data.copy()
    audience = (
        "test-audience" if settings.ENVIRONMENT == "test" else settings.TOKEN_AUDIENCE
    )

    to_encode.update(
        {
            "jti": jti,
            "access_jti": access_jti,  # Store the actual access token's JTI
            "type": "refresh",
            "exp": datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow(),
            "iss": settings.TOKEN_ISSUER,
            "aud": audience,
        }
    )
    return jwt.encode(
        to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
    )


def decode_token(token: str, token_type: str = settings.TOKEN_TYPE_ACCESS) -> Dict:
    """Decode and validate a token."""
    try:
        # Select appropriate secret key based on token type
        # This is safe as we're just comparing string constants for token types
        secret_key = (
            settings.SECRET_KEY
            if token_type == settings.TOKEN_TYPE_ACCESS
            else settings.REFRESH_SECRET_KEY
        )
        audience = (
            "test-audience"
            if settings.ENVIRONMENT == "test"
            else settings.TOKEN_AUDIENCE
        )

        # First decode and validate the token
        payload = jwt.decode(
            token, secret_key, algorithms=[settings.ALGORITHM], audience=audience
        )

        # Then check if it's blacklisted
        if "jti" in payload and payload["jti"] in _token_blacklist:
            raise InvalidTokenError("Token has been invalidated")

        if payload.get("type") != token_type:
            raise InvalidTokenError("Invalid token type")

        return payload

    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.InvalidAudienceError:
        raise InvalidTokenError("Invalid audience")
    except jwt.PyJWTError as e:
        raise InvalidTokenError(str(e))


def invalidate_token_by_jti(jti: str) -> None:
    """Add a token JTI to the blacklist."""
    _token_blacklist.add(jti)
    logger.info(f"Token {jti} added to blacklist")


def invalidate_token(token: str) -> None:
    """Decode and blacklist token by JTI, and optionally also blacklist its linked access_jti."""
    try:
        # Use the appropriate secret key based on token type
        unverified = jwt.decode(token, options={"verify_signature": False})
        token_type = unverified.get("type", settings.TOKEN_TYPE_ACCESS)
        secret_key = (
            settings.REFRESH_SECRET_KEY
            if token_type == settings.TOKEN_TYPE_REFRESH
            else settings.SECRET_KEY
        )

        # Properly verify the token before invalidating
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[settings.ALGORITHM],
            audience=(
                "test-audience"
                if settings.ENVIRONMENT == "test"
                else settings.TOKEN_AUDIENCE
            ),
        )

        jti = payload.get("jti")
        if jti:
            invalidate_token_by_jti(jti)
            if payload.get("type") == "refresh" and "access_jti" in payload:
                invalidate_token_by_jti(payload["access_jti"])

    except jwt.PyJWTError as e:
        raise InvalidTokenError(f"Could not invalidate token: {str(e)}")
