from typing import Any

from fastapi import status
from pydantic import BaseModel

from ...types_app import ResponseType


def _response(
    status_code: int,
    message: str,
    description: Any,
) -> ResponseType:
    class Message(BaseModel):
        detail: str = message

    return {status_code: {"model": Message, "description": description}}


def response_400(message: str, description: str | None = None) -> ResponseType:
    return _response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=message,
        description=description or message,
    )


def response_400_already_exists(name: str) -> ResponseType:
    return response_400(
        message=f"{name} already exists",
        description="The item already exists",
    )


def response_401(
    message: str = "Not authenticated",
    description: str = "User is not authenticated",
) -> ResponseType:
    return _response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=message,
        description=description,
    )


def response_403(
    message: str = "Admin access only",
    description: str = "User is not authorized",
) -> ResponseType:
    return _response(
        status_code=status.HTTP_403_FORBIDDEN,
        message=message,
        description=description,
    )


def response_404(name: str) -> ResponseType:
    return _response(
        status_code=status.HTTP_404_NOT_FOUND,
        message=f"{name} not found",
        description="The item was not found",
    )
