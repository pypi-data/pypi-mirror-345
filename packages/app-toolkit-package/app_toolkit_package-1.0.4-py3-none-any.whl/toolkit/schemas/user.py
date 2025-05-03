from pydantic import BaseModel, EmailStr

from ..types_app import NonEmptyStr
from .base import Base


# INPUT ===================================================
class BaseUserUpdate(BaseModel):
    first_name: NonEmptyStr | None = None
    last_name: NonEmptyStr | None = None
    phone_number: NonEmptyStr | None = None


class BaseUserCreate(BaseUserUpdate):
    email: EmailStr
    password: NonEmptyStr


# OUTPUT ==================================================
class BaseUserOut(BaseUserUpdate, Base):
    email: EmailStr


class BaseMe(Base):
    email: EmailStr
    full_name: NonEmptyStr
