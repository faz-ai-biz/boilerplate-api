from fastapi import APIRouter

from src.services.hello import get_hello_message

router = APIRouter(tags=["hello"])


@router.get("/hello")
def hello_world():
    return {"message": get_hello_message()}
