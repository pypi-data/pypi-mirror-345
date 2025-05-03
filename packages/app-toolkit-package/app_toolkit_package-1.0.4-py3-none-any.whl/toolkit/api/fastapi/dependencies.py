from typing import Annotated, Any

from fastapi import Depends

from ...config import cache_config, db_config
from ...repo.db import crud
from ...types_app import TypePK
from .utils import (
    get_client_info,
    set_headers_no_client_cache,
)

# HTTP dependencies
client_info = Annotated[
    dict[str, Any],
    Depends(get_client_info),
]
set_headers = Depends(set_headers_no_client_cache)

# Repos dependencies
redis = Annotated[
    cache_config.aioredis.Redis,
    Depends(cache_config.get_aioredis),
]
async_session = Annotated[
    db_config.AsyncSession,
    Depends(db_config.get_async_session),
]


# @catch_not_found
async def check_user(
    session: async_session,
    user_id: TypePK,
):
    from src.models import User

    await crud.exists(
        session,
        User,
        raise_not_found=True,
        id=user_id,
    )


existing_user = Depends(check_user)
