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


@router.get("/config", operation_id="getConfig")
async def config() -> dict:
    """
    Returns the version of the crypticorn library and the environment.
    """
    import importlib.metadata
    import os
    from dotenv import load_dotenv

    load_dotenv()
    try:
        crypticorn_version = importlib.metadata.version("crypticorn")
    except importlib.metadata.PackageNotFoundError:
        crypticorn_version = "not installed"
    return {
        "crypticorn": f"v{crypticorn_version}",
        "environment": os.getenv("API_ENV", "not set"),
    }
