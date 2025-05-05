from datetime import datetime
from typing import Literal
from fastapi import APIRouter

router = APIRouter(tags=["Status"], prefix="")


@router.get("/", operation_id="ping")
async def ping() -> str:
    """
    Returns 'OK' if the API is running.
    """
    return "OK"


@router.get("/time", operation_id="getTime")
async def time(type: Literal["iso", "unix"] = "iso") -> str:
    """
    Returns the current time in the specified format.
    """
    if type == "iso":
        return datetime.now().isoformat()
    else:
        return str(int(datetime.now().timestamp()))
