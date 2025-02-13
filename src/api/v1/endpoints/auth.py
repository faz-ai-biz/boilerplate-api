from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.v1.dependencies.auth import get_current_user
from src.core.config import settings
from src.core.exceptions import InvalidTokenError
from src.core.security import verify_password
from src.core.token_manager import (
    create_access_token,
    create_refresh_token,
    decode_token,
    invalidate_token,
    invalidate_token_by_jti,
)
from src.db.repositories import get_user_by_email
from src.db.session import get_db
from src.utils.logging import logger

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create tokens with user claims
    claims = {"user_id": user.id}
    access_token, access_jti = create_access_token(claims)  # Get both token and JTI
    refresh_token = create_refresh_token(
        claims, access_jti=access_jti
    )  # Pass the real access JTI

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        logger.info("Attempting to refresh token")
        payload = decode_token(token, token_type=settings.TOKEN_TYPE_REFRESH)

        # Invalidate old access token JTI if present
        old_access_jti = payload.get("access_jti")
        if old_access_jti:
            logger.info(f"Invalidating old access token with JTI: {old_access_jti}")
            invalidate_token_by_jti(old_access_jti)

        # Invalidate the used refresh token
        logger.info("Invalidating used refresh token")
        invalidate_token(token)

        # Create new token pair
        new_access_token, new_access_jti = create_access_token(
            {"user_id": payload.get("user_id")}
        )
        new_refresh_token = create_refresh_token(
            {"user_id": payload.get("user_id")}, access_jti=new_access_jti
        )
        logger.info(f"Created new access token for user {payload.get('user_id')}")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    except InvalidTokenError as e:
        logger.error(f"Invalid token error during refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.post("/verify")
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token, token_type=settings.TOKEN_TYPE_ACCESS)
        return {"status": "success", "user_id": payload.get("user_id")}
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout endpoint that invalidates the current token."""
    try:
        # Invalidate the current access token
        invalidate_token(token)
        logger.info("Token invalidated during logout")
        return {"status": "success", "detail": "Successfully logged out"}
    except InvalidTokenError as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@router.get("/protected")
async def protected_route(current_user: Dict = Depends(get_current_user)):
    """A protected route that requires a valid access token."""
    return {
        "status": "success",
        "message": "You have access to protected content",
        "user_id": current_user["id"],
    }
