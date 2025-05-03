from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Doc

from ...models.user import BaseUser as User
from ...types_app import NonEmptyStr
from ..config import auth_conf
from ..schemas import UserLoginForm
from .exceptions import AdminAccessOnly

jwt_token = Annotated[
    NonEmptyStr,
    Depends(OAuth2PasswordBearer(tokenUrl=auth_conf.TOKEN_URL)),
    # Doc(""),
]
login_form_data = Annotated[
    UserLoginForm,
    Depends(OAuth2PasswordRequestForm),
    # Doc(""),
]


from ..services.user import authenticate_user, get_current_user  # noqa

authenticated_user = Annotated[
    User,
    Depends(authenticate_user),
    Doc(
        """
        Dependency is for `/login` endpoint to obtain a token
        for existing user with verified password.
        """
    ),
]
current_user = Annotated[
    User,
    Depends(get_current_user),
    # Doc(""),
]


def get_admin(user: current_user):
    if user.admin:
        return user
    raise AdminAccessOnly


admin = Annotated[
    User,
    Depends(get_admin),
    # Doc(""),
]
admin_access_only = admin.__metadata__
