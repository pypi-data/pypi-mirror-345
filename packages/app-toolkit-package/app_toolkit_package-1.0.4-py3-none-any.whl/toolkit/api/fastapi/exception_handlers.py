from fastapi import Request
from fastapi.responses import JSONResponse
from src.main import app

from ...repo.db.exceptions import AlreadyExists, NotFound


@app.exception_handler(NotFound)
async def not_found_exception_handler(
    request: Request,
    exc: NotFound,
):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.msg},
    )


@app.exception_handler(AlreadyExists)
async def already_exists_exception_handler(
    request: Request,
    exc: AlreadyExists,
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )
