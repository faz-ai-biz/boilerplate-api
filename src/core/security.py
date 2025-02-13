import re
from datetime import datetime, timedelta
from typing import Dict, Set

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import FastAPI, HTTPException, Request
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import settings
from src.core.exceptions import PasswordTooWeakException
from src.utils.logging import logger

# Initialize security tools with consistent configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hasher = PasswordHasher()


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using Argon2."""
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength requirements.
    Returns True if password is strong enough, raises PasswordTooWeakException otherwise.
    """
    if len(password) < 8:
        raise PasswordTooWeakException("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        raise PasswordTooWeakException(
            "Password must contain at least one uppercase letter"
        )

    if not re.search(r"[a-z]", password):
        raise PasswordTooWeakException(
            "Password must contain at least one lowercase letter"
        )

    if not re.search(r"\d", password):
        raise PasswordTooWeakException("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise PasswordTooWeakException(
            "Password must contain at least one special character"
        )

    return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/v1/auth/login":
            client_ip = request.client.host
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=settings.LOGIN_RATE_LIMIT_WINDOW)

            # Clean old requests
            if client_ip in self.requests:
                self.requests[client_ip] = [
                    req_time
                    for req_time in self.requests[client_ip]
                    if req_time > window_start
                ]

            # Check rate limit
            if (
                client_ip in self.requests
                and len(self.requests[client_ip]) >= settings.LOGIN_RATE_LIMIT_REQUESTS
            ):
                raise HTTPException(
                    status_code=429, detail="Too many requests. Please try again later."
                )

            # Record request
            if client_ip not in self.requests:
                self.requests[client_ip] = []
            self.requests[client_ip].append(now)

        return await call_next(request)


def setup_security(app: FastAPI) -> None:
    """Setup security middleware and configurations for the FastAPI app."""
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    logger.info("Security middleware and configurations have been set up")
