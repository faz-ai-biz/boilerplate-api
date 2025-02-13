from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.api.v1.dependencies.auth import get_current_user
from src.core.exceptions import PasswordTooWeakException
from src.db.session import get_db
from src.services.user import user_create_service, user_read_service


class UserCreate(BaseModel):
    email: EmailStr
    password: str


router = APIRouter(tags=["users"])


@router.get("/me", response_model=dict)
@router.get("/users/me", response_model=dict)
async def get_current_user_info(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user information"""
    # Fetch fresh user data from DB using the validated user_id
    db_user = user_read_service(db, current_user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": db_user.id, "email": db_user.email}


@router.post("/users")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = user_create_service(db, user.email, user.password)
        if not db_user:
            raise HTTPException(status_code=400, detail="User creation failed")
        return {"id": db_user.id, "email": db_user.email}
    except PasswordTooWeakException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_read_service(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": db_user.id, "email": db_user.email}
