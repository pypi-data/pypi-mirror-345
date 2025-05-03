from fastapi import APIRouter, status

from ..config import auth_conf
from ..schemas import Token
from ..services.token import create_access_token
from .dependencies import authenticated_user

router = APIRouter(
    prefix=auth_conf.TOKEN_URL,
    tags=["Authentication"],
)


@router.post(
    "",
    summary="",
    description="",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
)
async def login_user(user: authenticated_user):
    # creturn Token(access_token=create_access_token(user))
    return {"access_token": create_access_token(user)}
