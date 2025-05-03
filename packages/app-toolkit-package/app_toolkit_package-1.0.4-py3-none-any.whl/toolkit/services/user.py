from ..auth.services.password import hash_password
from ..types_app import _AS
from .db_service import DBService


class BaseUserService(DBService):
    async def create(
        self,
        *,
        session: _AS | None = None,
        obj=None,
        **create_data,
    ):
        if obj is None:
            obj = self.model(**create_data)
        obj.password = hash_password(obj.password)
        return await super().create(session=session, obj=obj)
