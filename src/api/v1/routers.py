from fastapi import APIRouter


from .endpoints.hello import router as hello_router
from .endpoints.metrics import router as metrics_router


api_router = APIRouter()

api_router.include_router(hello_router, prefix="/api/v1")
api_router.include_router(metrics_router, prefix="/api/v1")
