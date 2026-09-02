import socket
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from ..config import Settings, get_settings

router = APIRouter()


@router.get("/")
def read_root(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    return {
        "message": "hello",
        "path": request.url.path,
        "host": socket.gethostname(),
        "service": settings.service_name,
        "version": settings.app_version,
    }
