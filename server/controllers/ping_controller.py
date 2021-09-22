from fastapi import APIRouter, Response
from server.controllers import session_exception_handler
from fastapi import status


router = APIRouter()
ping_router = dict(
    router=router,
    prefix="/ping",
    tags=["Ping"],
)


@router.get("", status_code=status.HTTP_204_NO_CONTENT)
async def ping():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

