from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.hello import router as hello_router
from .endpoints.metrics import router as metrics_router
from .endpoints.users import router as users_router

api_router = APIRouter()

api_router.include_router(hello_router, prefix="/api/v1")
api_router.include_router(metrics_router, prefix="/api/v1")
api_router.include_router(users_router, prefix="/api/v1")
api_router.include_router(auth_router, prefix="/api/v1")
