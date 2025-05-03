from functools import partial

from fastapi import HTTPException, status

AdminAccessOnly = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Admin access only",
)

exception_401 = partial(
    HTTPException,
    status_code=status.HTTP_401_UNAUTHORIZED,
    headers={"WWW-Authenticate": "Bearer"},
)
InvalidTokenPayload = exception_401(
    detail="Could not validate credentials",
)
ExpiredToken = exception_401(
    detail="Token has been expired",
)
IncorrectLoginCredentials = exception_401(
    detail="Incorrect email or password",
)
